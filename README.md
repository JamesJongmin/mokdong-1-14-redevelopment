# 목동 신시가지 1~14단지 재건축 트래커

레이스(진행 속도)·사업성·관심도 **3축 점수로 14개 단지를 매일 줄 세우는 단일 대시보드**.
서버 없이 GitHub Pages로 호스팅되는 정적 사이트이며, **GitHub Action(cron)이 매일 1회 데이터를 자동 갱신**합니다.

---

## 폴더 구조

```
mokdong-1-14-redevelopment/
├─ index.html                  # 대시보드(3줄 요약·3축 랭킹·캘린더·뉴스·단지 카드)
├─ complex.html                # 단지 상세 템플릿 (complex.html?id=N, 14단지 공용)
├─ data.json                   # 단지 데이터 + 점수(빌드 스크립트가 갱신)
├─ news.json                   # 최근 30일 뉴스(자동 수집)
├─ scripts/
│  ├─ fetch_news.py            # 구글 뉴스 RSS 수집 → news.json (API 키 불필요)
│  └─ build_data.py            # 레이스·관심도·3줄요약 재계산 → data.json
├─ .github/workflows/
│  └─ daily-update.yml         # 매일 08:00 KST 자동 실행·커밋
└─ README.md
```

## 매일 자동 갱신 흐름

```
매일 08:00 KST (cron)
  → fetch_news.py : '목동 재건축' 뉴스 수집·단지 태깅 → news.json
  → build_data.py : 점수 재계산 + "오늘의 3줄 요약" 생성 → data.json
  → 변경분 자동 commit & push → Pages 재배포
index.html / complex.html 이 data.json·news.json 을 읽어 화면을 그림
```

## 점수 방법론

- **레이스**: 정비 단계를 표준 점수로 환산(정비구역 지정 10 → 시공사 선정 60 → 사업시행인가 75 → 준공 100). `data.json`의 `stage_scores` 표 참고.
- **사업성**: 대지지분(35%)·추정 비례율(25%)·현 용적률(15%, 낮을수록↑)·입지(15%)·규모 효율(10%) 가중합. 구조값 미확정 단지는 잠정 `feasibility_seed` 사용.
- **관심도**: 최근 30일 뉴스 언급 빈도 기반(콜드스타트 시 `interest_seed`). 향후 네이버 검색지수·실거래량 추가 예정.

## 데이터 수정(반복 작업)

- **단계 변동**(시공사 선정/사업시행인가 등): `data.json`의 해당 단지 `race_stage_key`만 바꾸면 점수·타임라인·랭킹이 자동 반영됩니다. (키 목록은 `stage_scores` 참고)
- **구조값 확정**: `land_share_avg`·`far_current`·`expected_ratio` 등을 채우면 사업성 점수가 시드값 대신 가중합으로 계산됩니다.
- **다음 마일스톤**: `next_milestone`의 `event`/`target` 수정 → 캘린더 반영.

> 단계 변동은 오탐 방지를 위해 **뉴스 자동 감지 → 사람이 확정** 2단계 원칙을 권장합니다(현재는 수동 확정).

## 로컬에서 미리 보기

```bash
python scripts/fetch_news.py     # news.json 생성
python scripts/build_data.py     # data.json 점수 재계산
python -m http.server 8000       # http://localhost:8000 접속 (file:// 은 fetch 제한)
```

## 면책

공개 정보를 정리하는 **비공식 정보 트래커**입니다. 모든 수치는 추정·비공식이며 투자 권유·법적 자문이 아닙니다. 정비 단계·분담금·일정은 각 조합/신탁 및 관계기관 공식 고시문으로 확인하세요. 목동 일대는 토지거래허가 등 거래 제약이 있을 수 있습니다.
