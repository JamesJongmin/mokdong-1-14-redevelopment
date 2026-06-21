# 목동 신시가지 1~14단지 재건축 Watch

서울 양천구 목동 신시가지 1~14단지 재건축 **진행상황 추적 + 정기 리포트** 사이트.
서버 없이 GitHub Pages로 무료 호스팅되는 정적 사이트입니다. (coffeemarket.info와 동일한 구조)

---

## 폴더 구조

```
mokdong-1-14-redevelopment/
├─ index.html                      # 홈페이지 (히어로·사업단계·단지현황·리포트 목록)
├─ reports.json                    # 리포트 인덱스 (자동 생성 — 직접 수정하지 않음)
├─ Reports/
│  └─ 2026/06/2026-06-21-progress.html   # 개별 리포트(샘플)
├─ templates/
│  └─ report-template.html         # 새 리포트 만들 때 복사해서 사용
├─ scripts/
│  └─ build_reports.py             # reports.json 자동 생성 스크립트
├─ .github/workflows/
│  └─ update-reports.yml           # push 시 reports.json 자동 갱신(GitHub Action)
└─ README.md
```

## 작동 방식 (한 문장)

리포트 HTML 상단의 **`REPORT_META`** 블록을 GitHub Action이 읽어 **`reports.json`** 을 자동으로 만들고, 홈페이지(`index.html`)가 그 JSON을 불러와 목록·최신글을 그립니다. → **리포트 파일만 추가/push 하면 홈에 자동 등록됩니다.**

---

## 처음 1회: GitHub Pages로 배포하기

1. GitHub에 로그인 → **New repository** → 이름 예: `mokdong-1-14-redevelopment` (Public).
2. 이 폴더의 내용을 그 저장소에 올립니다.
   - 가장 쉬운 방법: 저장소 페이지의 **Add file → Upload files** 로 폴더 내용을 드래그해서 업로드 → Commit.
   - 또는 Git이 익숙하면:
     ```bash
     cd "이 폴더"
     git init
     git add .
     git commit -m "first commit"
     git branch -M main
     git remote add origin https://github.com/<사용자명>/mokdong-1-14-redevelopment.git
     git push -u origin main
     ```
3. 저장소 → **Settings → Pages** → Source를 **Deploy from a branch**, Branch를 **main / (root)** 로 지정 → Save.
4. 1~2분 뒤 `https://<사용자명>.github.io/mokdong-1-14-redevelopment/` 에서 사이트가 열립니다.

> ⚠️ Action이 reports.json을 push 하려면: 저장소 **Settings → Actions → General → Workflow permissions** 에서 **"Read and write permissions"** 를 켜 주세요.

---

## 새 리포트 추가하기 (반복 작업)

1. `templates/report-template.html` 을 복사해 `Reports/연/월/YYYY-MM-DD-제목.html` 로 저장.
2. 파일 상단 **`REPORT_META`** 를 채웁니다(유효한 JSON):
   - `title`, `date`(YYYY-MM-DD), `type`(`progress`/`in-depth`/`notice`), `summary`, `tags`.
3. 본문(`<body>`)을 작성.
4. GitHub에 push(또는 Upload files) → Action이 자동으로 `reports.json` 갱신 → 홈에 등록됨.

> 로컬에서 미리 인덱스를 만들어 보려면: `python scripts/build_reports.py`

### 리포트 유형(type)
| type | 표시 | 용도 |
|------|------|------|
| `progress` | 진행상황 | 주간/수시 진행 브리핑 |
| `in-depth` | 심층분석 | 분담금·사업성·조합 이슈 등 심층 |
| `notice` | 공지 | 조합 공지·총회 결과·일정 |

---

## 자주 손대는 곳

- **단지별 현황 카드**: `index.html` 의 `COMPLEXES` 배열(단계/방식/비고)을 수정.
- **사업 단계 타임라인**: `index.html` 의 `#timeline` 섹션에서 `done`/`now` 클래스로 현재 단계 표시.
- **상단 통계·연락처·문구**: `index.html` 히어로/푸터.
- **디자인 색상**: 각 파일 상단 `:root` 의 CSS 변수(`--brand`, `--brick` 등).

## 나중에: 커스텀 도메인 연결

도메인을 구매했다면 저장소 루트에 `CNAME` 파일(내용: `yourdomain.com` 한 줄)을 추가하고, 도메인 DNS에서 GitHub Pages IP/CNAME을 설정한 뒤 Settings → Pages → Custom domain에 입력하면 됩니다.

---

## 면책

본 사이트는 공개 정보를 정리하는 **비공식 정보 트래커**입니다. 정확성을 보장하지 않으며 투자 권유·법적 자문이 아닙니다. 정확한 사업 단계·일정·분담금은 각 조합/신탁 및 관계기관 공식 자료로 확인하세요.
