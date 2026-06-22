#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_news.py — 구글 뉴스 RSS에서 목동 재건축 뉴스 자동 수집 (표준 라이브러리만 사용, API 키 불필요)

하는 일:
  - "목동 재건축", "목동 신시가지 재건축" 등 검색 RSS 수집
  - 최근 30일 기사만 유지, 링크 기준 중복 제거
  - 제목으로 단지 태깅(목동 N단지 / N단지)
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

QUERIES = [
    "목동 재건축",
    "목동 신시가지 재건축",
    "목동 시공사 선정",
]
WINDOW_DAYS = 30
MAX_ITEMS = 60
UA = "Mozilla/5.0 (compatible; MokdongWatchBot/1.0; +https://github.com/)"

COMPLEX_RE = re.compile(r"(?:목동\s*)?(?:신시가지\s*)?(\d{1,2})\s*단지")


def fetch_rss(query):
    url = ("https://news.google.com/rss/search?q="
           + urllib.parse.quote(query)
           + "&hl=ko&gl=KR&ceid=KR:ko")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def tag_complexes(text):
    ids = set()
    for m in COMPLEX_RE.finditer(text or ""):
        n = int(m.group(1))
        if 1 <= n <= 14:
            ids.add(n)
    return sorted(ids)


def parse_items(xml_bytes):
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
        out.append({
            "title": title, "link": link, "source": source,
            "published": published.isoformat(timespec="seconds") if published else None,
            "_pub_dt": published,
            "complexes": tag_complexes(title),
        })
    return out


def main():
    cutoff = datetime.now(KST) - timedelta(days=WINDOW_DAYS)
    seen, items = set(), []
    for q in QUERIES:
        try:
            xb = fetch_rss(q)
        except Exception as e:
            print(f"[warn] '{q}' 수집 실패: {e}", file=sys.stderr)
            continue
        for it in parse_items(xb):
            key = it["link"] or it["title"]
            if not key or key in seen:
                continue
            if it["_pub_dt"] and it["_pub_dt"] < cutoff:
                continue
            seen.add(key)
            items.append(it)

    # 최신순 정렬 후 정리
    items.sort(key=lambda x: x["_pub_dt"] or datetime.min.replace(tzinfo=KST),
               reverse=True)
    items = items[:MAX_ITEMS]
    for it in items:
        it.pop("_pub_dt", None)

    payload = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "window_days": WINDOW_DAYS,
        "count": len(items),
        "items": items,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"news.json 갱신 완료 · {len(items)}건 수집")


if __name__ == "__main__":
    main()
