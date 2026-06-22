#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_data.py — 목동 트래커 점수 재계산 엔진 (표준 라이브러리만 사용)

하는 일:
  1) data.json 읽기
  2) news.json(있으면) 읽어 단지별 30일 언급수(news_mentions_30d) 갱신
  3) 레이스 점수 = 단계점수 + 보너스
  4) 사업성 점수 = (구조값 있으면 가중합, 없으면 시드값)
  5) 관심도 점수 = 시드 + 뉴스 언급 기반(콜드스타트 시 시드)
  6) "오늘의 3줄 요약" 생성, updated_at 갱신
  7) data.json 덮어쓰기 (사람이 관리하는 필드 race_stage_key/구조값/notes 는 보존)

사용:  python scripts/build_data.py
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data.json")
NEWS = os.path.join(ROOT, "news.json")
KST = timezone(timedelta(hours=9))


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def feasibility_score(c, weights):
    """구조값(대지지분/용적률/비례율 등)이 채워지면 가중합, 아니면 시드값 사용."""
    ls = c.get("land_share_avg")
    if ls is None:
        return c.get("feasibility_seed", 0)
    w = weights["feasibility"]
    # 0~100 정규화(잠정 기준값 — 실데이터 확보 시 조정)
    land = clamp((ls / 25.0) * 100)                      # 25평 지분을 만점 기준
    ratio = clamp(c.get("expected_ratio") or 100)        # 비례율 100%≈기준
    far_c = c.get("far_current") or 130
    far_inv = clamp((1 - (far_c - 100) / 150) * 100)     # 용적률 낮을수록 ↑
    loc = c.get("location_premium", 70)
    scale = c.get("scale_efficiency", 70)
    s = (land * w["land_share"] + ratio * w["expected_ratio"] +
         far_inv * w["far_current_inverse"] + loc * w["location_premium"] +
         scale * w["scale_efficiency"])
    return round(clamp(s))


def interest_score(c, any_news):
    seed = c.get("interest_seed", 50)
    if not any_news:
        return seed  # 콜드스타트: 뉴스 데이터 없으면 시드 사용
    mentions = c.get("news_mentions_30d", 0)
    news_derived = clamp(mentions * 8)   # 12건 ≈ 만점 근처
    return round(clamp(0.4 * seed + 0.6 * news_derived))


def main():
    data = load(DATA)
    if not data:
        print("data.json 을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    stage_scores = data["stage_scores"]
    weights = data["meta"].get("weights", {"feasibility": {
        "land_share": 0.35, "expected_ratio": 0.25, "far_current_inverse": 0.15,
        "location_premium": 0.15, "scale_efficiency": 0.10}})

    # 1) 뉴스 언급수 반영
    news = load(NEWS, {"items": []})
    items = news.get("items", [])
    counts = {c["complex_id"]: 0 for c in data["complexes"]}
    for it in items:
        for cid in it.get("complexes", []):
            if cid in counts:
                counts[cid] += 1
    any_news = len(items) > 0
    for c in data["complexes"]:
        c["news_mentions_30d"] = counts.get(c["complex_id"], 0)

    # 2) 점수 재계산
    for c in data["complexes"]:
        key = c.get("race_stage_key")
        base = stage_scores.get(key, {}).get("score", 0)
        c["race_stage"] = stage_scores.get(key, {}).get("label", key or "미정")
        c["race_score"] = round(clamp(base + c.get("race_bonus", 0)))
        c["feasibility_score"] = feasibility_score(c, weights)
        c["interest_score"] = interest_score(c, any_news)

    # 3) 오늘의 3줄 요약 (각 축 1위)
    def top(metric):
        return max(data["complexes"], key=lambda x: x.get(metric, 0))
    r, f, i = top("race_score"), top("feasibility_score"), top("interest_score")
    data["meta"]["summary3"] = {
        "race": {"name": r["name"], "score": r["race_score"],
                 "label": r["race_stage"]},
        "feasibility": {"name": f["name"], "score": f["feasibility_score"],
                        "type": f.get("feasibility_type", "")},
        "interest": {"name": i["name"], "score": i["interest_score"],
                     "mentions": i.get("news_mentions_30d", 0)},
    }

    # 4) 타임스탬프
    data["meta"]["updated_at"] = datetime.now(KST).isoformat(timespec="seconds")

    with open(DATA, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print("data.json 갱신 완료 ·",
          f"레이스1위 {r['name']}({r['race_score']}) ·",
          f"사업성1위 {f['name']}({f['feasibility_score']}) ·",
          f"관심도1위 {i['name']}({i['interest_score']})")


if __name__ == "__main__":
    main(