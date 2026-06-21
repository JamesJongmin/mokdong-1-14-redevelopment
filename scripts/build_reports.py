#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reports/ 폴더의 모든 리포트 HTML에서 REPORT_META 블록을 읽어
reports.json(홈페이지가 읽는 인덱스)을 자동 생성한다.

로컬 실행:  python scripts/build_reports.py
GitHub:    .github/workflows/update-reports.yml 가 push 시 자동 실행
"""
import os, re, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(ROOT, "Reports")
OUT = os.path.join(ROOT, "reports.json")

META_RE = re.compile(r"<!--\s*REPORT_META\s*(\{.*?\})\s*REPORT_META\s*-->", re.S)

def collect():
    items = []
    if not os.path.isdir(REPORTS_DIR):
        return items
    for dirpath, _, files in os.walk(REPORTS_DIR):
        for fn in files:
            if not fn.lower().endswith(".html"):
                continue
            if "test" in fn.lower():
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                html = f.read()
            m = META_RE.search(html)
            if not m:
                print(f"  [skip] REPORT_META 없음: {fn}")
                continue
            try:
                meta = json.loads(m.group(1))
            except json.JSONDecodeError as e:
                print(f"  [ERROR] META JSON 파싱 실패: {fn} -> {e}")
                continue
            # 홈페이지가 쓰는 상대 경로(link) 자동 부여
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            meta["link"] = rel
            items.append(meta)
    # 날짜 내림차순(최신 먼저)
    items.sort(key=lambda r: r.get("date", ""), reverse=True)
    return items

def main():
    reports = collect()
    data = {"generated": True, "count": len(reports), "reports": reports}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"reports.json 생성 완료: {len(reports)}건")
    for r in reports:
        print(f"  - {r.get('date')} [{r.get('type')}] {r.get('title')}")

if __name__ == "__main__":
    main()
