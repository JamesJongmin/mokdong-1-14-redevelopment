#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_news.py — 구글 뉴스 RSS에서 목동 재건축 뉴스 자동 수집 (표준 라이브러리만 사용, API 키 불필요)

하는 일:
  - 일반 쿼리("목동 재건축" 등) + 단지별 쿼리(1~14단지) RSS 수집
  - 최근 30일 기사만 유지, 링크 기준 중복 제거(태그 병합)
  - 제목으로 단지 태깅, 제목에 번호가 없으면 '단지별 쿼리' 출처로 보완 태깅
  - 단지별 상한(PER_CAP)으로 특정 단지 기사 홍수가 다른 단지를 밀어내지 않게 공정 분배
  - news.json 으로 저장 (build_data.py 가 읽어 관심도 점수에 반영)

사용:  python scripts/fetch_news.py
"""
import json, os, re, sys
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "news.json")
KST = timezone(timedelta(hours=9))

# 일반 쿼리(전체 흐름) — 단지 미상도 수집
GENERAL_QUERIES = [
    "목동 재건축",
    "목동 신시가지 재건축",
    "목동 시공사 선정",
    "목동 신시가지 조합",
]
# 단지별 쿼리 — 각 단지의 개별 뉴스를 확실히 끌어오기 위함
COMPLEX_QUERIES = {n: f"목동 신시가지 {n}단지" for n in range(1, 15)}

WINDOW_DAYS = 30
PER_CAP = 18          # 단지당 저장 상한(공정 분배)
GENERAL_CAP = 18      # 단지 미상(untagged) 기사 저장 상한
MAX_ITEMS = 180       # 전체 저장 상한
UA = "Mozilla/5.0 (compatible; MokdongWatchBot/1.0; +https://github.com/)"

COMPLEX_RE = re.compile(r"(?:목동\s*)?(?:신시가지\s*)?(\d{1,2})\s*단지")


def fetch_rss(query):
    url = ("https://news.google.com/rss/search?q="
           + urllib.parse.quote(query)
           + "&hl=ko&gl=KR&ceid=KR:ko")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def tag_from_title(text):
    ids = set()
    for m in COMPLEX_RE.finditer(text or ""):
        n = int(m.group(1))
        if 1 <= n <= 14:
            ids.add(n)
    return ids


def parse_items(xml_bytes, origin_cid):
    """origin_cid: 이 RSS가 단지별 쿼리에서 왔으면 그 단지 번호(보완 태깅용), 아니면 None."""
    out = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return out
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        src_el = item.find("source")
        source = (src_el.text.strip() if src_el is not None and src_el.text else "")
        published = None
        if pub:
            try:
                published = parsedate_to_datetime(pub).astimezone(KST)
            except Exception:
                published = None
        tags = tag_from_title(title)
        # 제목에 단지 번호가 없으나 목동/신시가지 기사이고, 단지별 쿼리 출처면 보완 태깅
        if not tags and origin_cid and ("목동" in title or "신시가지" in title):
            tags = {origin_cid}
        out.append({
            "title": title, "link": link, "source": source,
            "published": published.isoformat(timespec="seconds") if published else None,
            "_pub_dt": published,
            "complexes": sorted(tags),
        })
    return out


def main():
    cutoff = datetime.now(KST) - timedelta(days=WINDOW_DAYS)
    by_key = {}  # link/title -> item (태그 병합)

    def ingest(items):
        for it in items:
            key = it["link"] or it["title"]
            if not key:
                continue
            if it["_pub_dt"] and it["_pub_dt"] < cutoff:
                continue
            if key in by_key:
                # 중복: 태그 병합(여러 쿼리에서 잡힌 경우)
                merged = set(by_key[key]["complexes"]) | set(it["complexes"])
                by_key[key]["complexes"] = sorted(merged)
            else:
                by_key[key] = it

    failures = 0
    # 일반 쿼리
    for q in GENERAL_QUERIES:
        try:
            ingest(parse_items(fetch_rss(q), None))
        except Exception as e:
            failures += 1
            print(f"[warn] '{q}' 수집 실패: {e}", file=sys.stderr)
    # 단지별 쿼리
    for cid, q in COMPLEX_QUERIES.items():
        try:
            ingest(parse_items(fetch_rss(q), cid))
        except Exception as e:
            failures += 1
            print(f"[warn] '{q}' 수집 실패: {e}", file=sys.stderr)

    items = list(by_key.values())
    items.sort(key=lambda x: x["_pub_dt"] or datetime.min.replace(tzinfo=KST),
               reverse=True)

    # 공정 분배: 단지당 PER_CAP, untagged는 GENERAL_CAP, 전체 MAX_ITEMS
    kept, per_count, gen_count = [], {n: 0 for n in range(1, 15)}, 0
    for it in items:
        tags = it["complexes"]
        if tags:
            if all(per_count[t] >= PER_CAP for t in tags):
                continue
            for t in tags:
                per_count[t] = per_count.get(t, 0) + 1
        else:
            if gen_count >= GENERAL_CAP:
                continue
            gen_count += 1
        kept.append(it)
        if len(kept) >= MAX_ITEMS:
            break

    for it in kept:
        it.pop("_pub_dt", None)

    payload = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "window_days": WINDOW_DAYS,
        "count": len(kept),
        "items": kept,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tagged = sum(1 for it in kept if it["complexes"])
    print(f"news.json 갱신 완료 · {len(kept)}건 수집 (태깅 {tagged}건) · 쿼리실패 {failures}건")


if __name__ == "__main__":
    main()
