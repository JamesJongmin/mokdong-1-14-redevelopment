# 설치/배포 안내 (한 번만)

이 폴더의 파일들을 기존 저장소 `JamesJongmin/mokdong-1-14-redevelopment`에 올리면 됩니다.

## 1) 파일 업로드
저장소 페이지 → **Add file → Upload files** → 이 폴더의 내용 전부 드래그 → **Commit**.
- `index.html`은 기존 파일을 **덮어쓰기**합니다(새 대시보드).
- `data.json`, `news.json`, `complex.html`, `scripts/`, `.github/workflows/daily-update.yml`은 신규 추가됩니다.
- 기존 `Reports/`, `templates/`, `reports.json`, `update-reports.yml`은 그대로 두면 됩니다(별개 기능).

> ⚠️ `.github/workflows/` 폴더는 드래그 업로드가 안 될 수 있습니다. 이 경우 **Add file → Create new file**에서 경로에 `.github/workflows/daily-update.yml`을 직접 입력하고 내용을 붙여넣으세요.

## 2) Action 쓰기 권한 켜기 (필수)
저장소 **Settings → Actions → General → Workflow permissions** → **"Read and write permissions"** 선택 → Save.
(이게 꺼져 있으면 매일 자동 커밋이 실패합니다.)

## 3) 첫 실행 (선택)
**Actions 탭 → Daily Update → Run workflow** 를 눌러 즉시 1회 실행하면, 바로 뉴스가 채워지고 점수가 갱신됩니다. 이후엔 매일 08:00(KST) 자동 실행됩니다.

## 4) 확인
`https://jamesjongmin.github.io/mokdong-1-14-redevelopment/` 에서 대시보드가 열리는지 확인.
(Pages는 이미 main/root로 배포 중이라 별도 설정 불필요.)

---

## 다음 단계(2차, API 키 필요)
아래는 시크릿 등록이 필요해 이번 1차에는 빠져 있습니다. 진행 원하시면 키 발급 후 알려주세요.
- **국토부 실거래가 API**: 단지별 거래량/시세 → 관심도·사업성 보강
- **네이버 데이터랩 API**: 단지별 검색지수 → 관심도 보강
- **분담금 시뮬레이터**: 평형·층 입력 → 추정 분담금(가정값 노출)
- **메일/슬랙 일일 요약 발송**
