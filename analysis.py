import os
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -------------------------------------------------------------
# 0. 한글 폰트 설정 (환경별 호환)
# -------------------------------------------------------------
import platform

if platform.system() == 'Windows':
  plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':  # Mac
  plt.rc('font', family='AppleGothic')
else:  # Linux / Colab fallback
  plt.rc('font', family='DejaVu Sans')
plt.rc('axes', unicode_minus=False)

os.makedirs('images', exist_ok=True)

# -------------------------------------------------------------
# 1. 데이터 로드 및 시트 병합 (조회수 + 순방문자수)
# -------------------------------------------------------------
file_name = '조회수_순방문자수_일간_2026-06-03_2026-08-31_20260901_152022.xlsx'

# [시트 1: 조회수]
df_views = pd.read_excel(file_name, sheet_name='조회수', skiprows=6)
df_views.columns = [
    '날짜',
    '요일',
    '조회수_전체',
    '조회수_피이웃',
    '조회수_서로이웃',
    '조회수_기타',
]

# [시트 2: 순방문자수]
df_visitors = pd.read_excel(file_name, sheet_name='순방문자수', skiprows=6)
df_visitors.columns = [
    '날짜',
    '요일',
    '순방문자수_전체',
    '순방문자수_피이웃',
    '순방문자수_서로이웃',
    '순방문자수_기타',
]

# 두 데이터 날짜 기준 병합 (Total 90일 x 8개 지표 = 720개 관측치)
df = pd.merge(
    df_views,
    df_visitors[[
        '날짜',
        '순방문자수_전체',
        '순방문자수_피이웃',
        '순방문자수_서로이웃',
        '순방문자수_기타',
    ]],
    on='날짜',
)

df['날짜'] = pd.to_datetime(df['날짜'])
df = df.sort_values('날짜').reset_index(drop=True)

# -------------------------------------------------------------
# 2. 시계열 파생 지표 및 통계 계산
# -------------------------------------------------------------
# (1) 7일 이동평균 (Moving Average)
df['MA7_조회수'] = df['조회수_전체'].rolling(window=7).mean()
df['MA7_순방문자수'] = df['순방문자수_전체'].rolling(window=7).mean()

# (2) 파생 지표
df['1인당_조회수'] = (df['조회수_전체'] / df['순방문자수_전체']).round(2)
df['검색_기타_비율(%)'] = (
    (df['조회수_기타'] / df['조회수_전체']) * 100
).round(1)

print('=== 통합 데이터 기본 정보 ===')
print(df.info())

# -------------------------------------------------------------
# 3. 시각화 생성 및 이미지 저장 (3개)
# -------------------------------------------------------------

# [시각화 1] 조회수 & 순방문자수 7일 이동평균 추세 비교
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(
    df['날짜'],
    df['조회수_전체'],
    label='일별 조회수',
    color='#5B9BD5',
    alpha=0.4,
    linestyle=':',
)
ax1.plot(
    df['날짜'],
    df['순방문자수_전체'],
    label='일별 순방문자수',
    color='#ED7D31',
    alpha=0.4,
    linestyle=':',
)
ax1.plot(
    df['날짜'],
    df['MA7_조회수'],
    label='조회수 7일 이동평균 (MA7)',
    color='#1F4E79',
    linewidth=2.5,
)
ax1.plot(
    df['날짜'],
    df['MA7_순방문자수'],
    label='순방문자 7일 이동평균 (MA7)',
    color='#C65911',
    linewidth=2.5,
)

ax1.set_title(
    '네이버 블로그 일별 트래픽 및 7일 이동평균 추세 (2026.06 ~ 2026.08)',
    fontsize=14,
    pad=12,
    fontweight='bold',
)
ax1.set_xlabel('날짜', fontsize=11)
ax1.set_ylabel('건수', fontsize=11)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(loc='upper left', fontsize=10)
plt.tight_layout()
plt.savefig('images/01_views_trend_ma7.png', dpi=300)
plt.close()

# [시각화 2] 요일별 평균 조회수 및 순방문자수 비교
weekday_order = ['월', '화', '수', '목', '금', '토', '일']
weekday_stats = (
    df.groupby('요일')[['조회수_전체', '순방문자수_전체']]
    .mean()
    .reindex(weekday_order)
)

fig, ax2 = plt.subplots(figsize=(10, 5))
x = np.arange(len(weekday_order))
width = 0.35
ax2.bar(
    x - width / 2,
    weekday_stats['조회수_전체'],
    width,
    label='평균 조회수',
    color='#2b82c9',
)
ax2.bar(
    x + width / 2,
    weekday_stats['순방문자수_전체'],
    width,
    label='평균 순방문자수',
    color='#f5a623',
)
ax2.set_xticks(x)
ax2.set_xticklabels(weekday_order)
ax2.set_title(
    '요일별 평균 조회수 및 순방문자수 비교',
    fontsize=14,
    pad=12,
    fontweight='bold',
)
ax2.set_xlabel('요일', fontsize=11)
ax2.set_ylabel('평균 건수', fontsize=11)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.legend(loc='upper right', fontsize=10)
plt.tight_layout()
plt.savefig('images/02_views_by_weekday.png', dpi=300)
plt.close()

# [시각화 3] 유입 경로별 일별 구성 추이
fig, ax3 = plt.subplots(figsize=(12, 6))
ax3.stackplot(
    df['날짜'],
    df['조회수_기타'],
    df['조회수_서로이웃'],
    df['조회수_피이웃'],
    labels=['기타/검색 유입', '서로이웃', '피이웃'],
    colors=['#4a90e2', '#50e3c2', '#b8e986'],
    alpha=0.85,
)
ax3.set_title(
    '유입 경로별 일별 조회수 구성 추이 (2026.06 ~ 2026.08)',
    fontsize=14,
    pad=12,
    fontweight='bold',
)
ax3.set_xlabel('날짜', fontsize=11)
ax3.set_ylabel('조회수 (건)', fontsize=11)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax3.grid(True, linestyle='--', alpha=0.5)
ax3.legend(loc='upper left', fontsize=10)
plt.tight_layout()
plt.savefig('images/03_traffic_source_ratio.png', dpi=300)
plt.close()

print('분석 완료: images 폴더에 3개 차트가 생성되었습니다.')