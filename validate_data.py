import os
import pandas as pd

# -------------------------------------------------------------
# 1. 파일 경로 설정
# -------------------------------------------------------------
file_name = 'data/조회수_순방문자수_일간_2026-06-03_2026-08-31_20260901_152022.xlsx'

# -------------------------------------------------------------
# 2. 데이터 로드 함수
# -------------------------------------------------------------
def load_blog_data(file_path):
    """
    네이버 블로그 통계 엑셀 파일에서 조회수/순방문자수 시트를 불러와
    날짜 기준으로 병합하는 함수
    """

    df_views = pd.read_excel(file_path, sheet_name='조회수', skiprows=6)
    df_views.columns = [
        '날짜',
        '요일',
        '조회수_전체',
        '조회수_피이웃',
        '조회수_서로이웃',
        '조회수_기타',
    ]

    df_visitors = pd.read_excel(file_path, sheet_name='순방문자수', skiprows=6)
    df_visitors.columns = [
        '날짜',
        '요일',
        '순방문자수_전체',
        '순방문자수_피이웃',
        '순방문자수_서로이웃',
        '순방문자수_기타',
    ]

    df = pd.merge(
        df_views,
        df_visitors[
            [
                '날짜',
                '순방문자수_전체',
                '순방문자수_피이웃',
                '순방문자수_서로이웃',
                '순방문자수_기타',
            ]
        ],
        on='날짜',
        how='inner'
    )

    df['날짜'] = pd.to_datetime(df['날짜'])
    df = df.sort_values('날짜').reset_index(drop=True)

    return df


# -------------------------------------------------------------
# 3. 데이터 유효성 검증 함수
# -------------------------------------------------------------
def validate_data(df):
    """
    날짜 누락, 결측치, 0값, 중복 날짜, 마지막 날 집계 상태 등을 확인한다.
    """

    print('==============================')
    print('데이터 유효성 검증 결과')
    print('==============================')

    # 1) 기본 정보
    print('\n[1] 기본 정보')
    print('시작일:', df['날짜'].min().date())
    print('종료일:', df['날짜'].max().date())
    print('총 행 수:', len(df))
    print('컬럼 목록:', list(df.columns))

    # 2) 날짜 누락 확인
    print('\n[2] 날짜 누락 확인')
    full_dates = pd.date_range(
        start=df['날짜'].min(),
        end=df['날짜'].max(),
        freq='D'
    )

    missing_dates = full_dates.difference(df['날짜'])

    print('전체 기간 기준 예상 날짜 수:', len(full_dates))
    print('실제 데이터 날짜 수:', df['날짜'].nunique())
    print('빠진 날짜 수:', len(missing_dates))

    if len(missing_dates) > 0:
        print('빠진 날짜 목록:')
        for date in missing_dates:
            print('-', date.date())
    else:
        print('빠진 날짜 없음')

    # 3) 중복 날짜 확인
    print('\n[3] 중복 날짜 확인')
    duplicated_dates = df[df['날짜'].duplicated()]

    print('중복 날짜 수:', len(duplicated_dates))

    if len(duplicated_dates) > 0:
        print(duplicated_dates[['날짜']])
    else:
        print('중복 날짜 없음')

    # 4) 결측치 확인
    print('\n[4] 결측치 확인')
    missing_values = df.isna().sum()
    print(missing_values)

    # 5) 0값 확인
    print('\n[5] 0값 확인')

    numeric_cols = [
        '조회수_전체',
        '조회수_피이웃',
        '조회수_서로이웃',
        '조회수_기타',
        '순방문자수_전체',
        '순방문자수_피이웃',
        '순방문자수_서로이웃',
        '순방문자수_기타',
    ]

    zero_counts = (df[numeric_cols] == 0).sum()
    print(zero_counts)

    zero_total_days = df[
        (df['조회수_전체'] == 0) | (df['순방문자수_전체'] == 0)
    ]

    print('\n전체 조회수 또는 전체 순방문자수가 0인 날짜 수:', len(zero_total_days))

    if len(zero_total_days) > 0:
        print(zero_total_days[['날짜', '조회수_전체', '순방문자수_전체']])
    else:
        print('전체 조회수/순방문자수 기준 0값 날짜 없음')

    # 6) 마지막 날 데이터 확인
    print('\n[6] 마지막 날 데이터 확인')

    last_day = df.iloc[-1]
    previous_7days = df.iloc[-8:-1]

    prev_7_avg_views = previous_7days['조회수_전체'].mean()
    prev_7_avg_visitors = previous_7days['순방문자수_전체'].mean()

    print('마지막 날짜:', last_day['날짜'].date())
    print('마지막 날 조회수:', last_day['조회수_전체'])
    print('직전 7일 평균 조회수:', round(prev_7_avg_views, 2))
    print('마지막 날 순방문자수:', last_day['순방문자수_전체'])
    print('직전 7일 평균 순방문자수:', round(prev_7_avg_visitors, 2))

    if last_day['조회수_전체'] < prev_7_avg_views * 0.5:
        print('주의: 마지막 날 조회수가 직전 7일 평균의 50% 미만입니다.')
        print('마지막 날 통계가 완전히 집계되지 않았을 가능성을 확인해야 합니다.')
    else:
        print('마지막 날 조회수가 직전 7일 평균 대비 과도하게 낮지는 않습니다.')

    # 7) 이상치 후보 확인: 상위 5%
    print('\n[7] 이상치 후보 확인')
    threshold = df['조회수_전체'].quantile(0.95)

    outliers = df[df['조회수_전체'] >= threshold][
        ['날짜', '요일', '조회수_전체', '순방문자수_전체']
    ]

    print('조회수 상위 5% 기준값:', round(threshold, 2))
    print('이상치 후보 날짜 수:', len(outliers))
    print(outliers)

    print('\n==============================')
    print('검증 완료')
    print('==============================')


# -------------------------------------------------------------
# 4. 실행
# -------------------------------------------------------------
if __name__ == '__main__':
    df = load_blog_data(file_name)
    validate_data(df)