# 네이버 블로그 트래픽 시계열 분석

2026년 6월~8월 네이버 블로그 일별 조회수·순방문자수 데이터를 분석한 프로젝트입니다.

## 폴더 구조

```
├── 조회수_순방문자수_일간_2026-06-03_2026-08-31_20260901_152022.xlsx  # 원본 데이터
├── analysis.py                # 분석 및 시각화 스크립트
├── requirements.txt           # 의존 라이브러리 목록
├── REPORT.md                  # 분석 리포트
└── images/                    # 시각화 결과 (스크립트 실행 시 자동 생성)
    ├── 01_views_trend_ma7.png
    ├── 02_views_by_weekday.png
    └── 03_traffic_source_ratio.png
```

## 실행 환경

- Python 3.10 이상

## 실행 방법

1. 이 저장소를 내려받거나 클론합니다.

   ```bash
   git clone <저장소 URL>
   cd <저장소 폴더>
   ```

2. (권장) 가상환경을 만들고 활성화합니다.

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. 의존 라이브러리를 설치합니다.

   ```bash
   pip install -r requirements.txt
   ```

4. 원본 데이터 엑셀 파일(`조회수_순방문자수_일간_2026-06-03_2026-08-31_20260901_152022.xlsx`)이 `analysis.py`와 같은 폴더에 있는지 확인합니다.

5. 분석 스크립트를 실행합니다.

   ```bash
   python analysis.py
   ```

6. 실행이 끝나면 `images/` 폴더에 시각화 3종(01~03번 png)이 생성되고, 터미널에 데이터 기본 정보(`df.info()`)가 출력됩니다. 이 이미지들은 `REPORT.md`에서 상대경로로 링크되어 있으므로, `images/` 폴더가 `REPORT.md`와 같은 위치에 있어야 리포트에서 그림이 정상적으로 열립니다.

## 한글 폰트 관련 참고

`analysis.py`는 OS별로 한글 폰트를 자동 지정합니다(Windows: Malgun Gothic, Mac: AppleGothic, Linux: DejaVu Sans). **Linux 환경에는 한글을 지원하는 폰트가 기본 설치되어 있지 않아 그래프의 한글 제목·범례가 깨질 수 있습니다.** Linux에서 실행할 경우 나눔고딕 등 한글 폰트를 별도로 설치한 뒤 `plt.rc('font', family='NanumGothic')`처럼 폰트명을 맞춰주세요.

## 데이터 출처 및 이용 안내

- 출처: 네이버 블로그 관리자 통계(비공개 개인 블로그 통계 페이지에서 직접 다운로드)
- 기간: 2026-06-03 ~ 2026-08-31 (일간, 90일)
- 이 데이터는 개인 블로그의 비공개 통계 자료로, 재배포 시 개인 식별 정보나 블로그 URL 등이 노출되지 않도록 주의가 필요합니다.
