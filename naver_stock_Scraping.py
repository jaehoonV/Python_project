import time
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from io import StringIO
import csv
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
url = 'https://finance.naver.com/item/sise_day.nhn?'

# KOSPI 데이터
ticker_list = []
with open('kospi_data_20241231.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        ticker_list.append({'ticker': row['ticker'], 'name': row['name']})

# 예측 데이터 처리 함수
def process_stock_data(ticker_info):
    ticker = ticker_info['ticker']
    name = ticker_info['name']

    dfs = []  # DataFrame을 담을 리스트
    code_url = f'{url}code={ticker}'

    for page in range(1, 8):
        page_url = f'{code_url}&page={page}'

        response = requests.get(page_url, headers=headers)
        html = bs(response.text, 'html.parser')
        html_table = html.select_one("table")  # 첫 번째 테이블만 가져옵니다.

        if html_table:  # 테이블이 존재할 경우에만 처리
            table_html = str(html_table)
            table = pd.read_html(StringIO(table_html))  # StringIO로 HTML 문자열 감싸기

            # 현재 데이터를 리스트에 추가
            dfs.append(table[0].dropna())

    # 모든 데이터를 하나의 DataFrame으로 병합
    df = pd.concat(dfs, ignore_index=True)

    # 날짜를 datetime 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y.%m.%d")

    # 정렬 (최근 날짜부터 오름차순으로)
    df = df.sort_values("날짜")

    # 5일, 20일, 60일 이동평균 계산
    df["MA5"] = df["종가"].rolling(window=5).mean()
    df["MA20"] = df["종가"].rolling(window=20).mean()
    df["MA60"] = df["종가"].rolling(window=60).mean()

    # 기준선 (26일 기준 고가, 저가의 평균) 계산
    df["Baseline"] = ((df["고가"].rolling(window=26).max() + df["저가"].rolling(window=26).min()) / 2).fillna(0).round().astype(int)
    # 전환선 (9일 기준 고가, 저가의 평균) 계산
    df["ConversionLine"] = ((df["고가"].rolling(window=9).max() + df["저가"].rolling(window=9).min()) / 2).fillna(0).round().astype(int)

    # 예측값 설정
    df["초단기예측"] = None  # 초기값 설정
    df["단기예측"] = None  # 초기값 설정
    df["전환예측"] = None  # 초기값 설정

    # 상승/하락 예측 조건 설정 (위의 예측 조건들 포함)

    # 초단기 예측값 설정
    condition_down = (df["MA5"] < df["MA20"]) & (df["MA5"].shift(1) >= df["MA20"].shift(1)) & (df["MA5"].shift(2) >= df["MA20"].shift(2))
    condition_up = (df["MA5"] > df["MA20"]) & (df["MA5"].shift(1) <= df["MA20"].shift(1)) & (df["MA5"].shift(2) <= df["MA20"].shift(2))

    # 단기 예측값 설정
    condition2_down = (df["MA20"] < df["MA60"]) & (df["MA20"].shift(1) >= df["MA60"].shift(1)) & (df["MA20"].shift(2) >= df["MA60"].shift(2))
    condition2_up = (df["MA20"] > df["MA60"]) & (df["MA20"].shift(1) <= df["MA60"].shift(1)) & (df["MA20"].shift(2) <= df["MA60"].shift(2))

    # 전환 예측값 설정
    condition3_down = (df["Baseline"] > df["ConversionLine"]) & (df["Baseline"].shift(1) <= df["ConversionLine"].shift(1)) & (df["Baseline"].shift(2) <= df["ConversionLine"].shift(2))
    condition3_up = (df["Baseline"] < df["ConversionLine"]) & (df["Baseline"].shift(1) >= df["ConversionLine"].shift(1)) & (df["Baseline"].shift(2) >= df["ConversionLine"].shift(2))

    df.loc[condition_down, "초단기예측"] = "하락"
    df.loc[condition_up, "초단기예측"] = "상승"
    df.loc[condition2_down, "단기예측"] = "하락"
    df.loc[condition2_up, "단기예측"] = "상승"
    df.loc[condition3_down, "전환예측"] = "하락"
    df.loc[condition3_up, "전환예측"] = "상승"

    # 마지막 3개의 행에서 '초단기예측', '단기예측', '전환예측'이 None이 아닌 경우 필터링
    filtered_df = df.tail(3)
    filtered_df = filtered_df.dropna(subset=["초단기예측", "단기예측", "전환예측"], how="all")
    output = []
    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            output.append({
                "날짜": row["날짜"],
                "종목명": name,
                "종목코드": ticker,
                "초단기예측": row["초단기예측"],
                "단기예측": row["단기예측"],
                "전환예측": row["전환예측"]
            })
    
    return output

# 병렬 처리
def fetch_and_process_data(ticker_list):
    all_output = []
    with ProcessPoolExecutor(max_workers=8) as executor:  # 최대 8개의 프로세스 사용
        futures = {executor.submit(process_stock_data, ticker_info): ticker_info for ticker_info in ticker_list}
        
        for future in as_completed(futures):
            result = future.result()
            all_output.extend(result)
    
    return all_output

# 실행
if __name__ == '__main__':
    start_time = time.time()  # 실행 시작 시간 기록

    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    print(f"실행시각 : {formatted_time} / 분석중...")

    output = fetch_and_process_data(ticker_list)

    # 초단기예측, 단기예측, 전환예측별 상승/하락 횟수 계산
    category_count = defaultdict(lambda: {'상승': 0, '하락': 0})

    # 날짜별 및 종목별 상승, 하락 횟수 계산
    date_count = defaultdict(lambda: {'상승': 0, '하락': 0, '종목': defaultdict(lambda: {'상승': 0, '하락': 0})})

    for record in output:
        date = record["날짜"]
        stock = record["종목명"]
        for key in ['초단기예측', '단기예측', '전환예측']:
            if record[key] == '상승':
                category_count[key]['상승'] += 1
                date_count[date]['상승'] += 1
                date_count[date]['종목'][stock]['상승'] += 1
            elif record[key] == '하락':
                category_count[key]['하락'] += 1
                date_count[date]['하락'] += 1
                date_count[date]['종목'][stock]['하락'] += 1

    # 결과 출력
    end_time = time.time()  # 실행 끝 시간 기록
    execution_time = end_time - start_time  # 실행 시간 계산

    print(f"\nExecution time: {execution_time:.2f} seconds")  # 실행 시간 출력
    print("Output:")
    print(output)
    print("예측별 상승, 하락 횟수:")
    for category, counts in category_count.items():
        print(f"{category}: 상승: {counts['상승']}, 하락: {counts['하락']}")

    print("\n날짜 및 종목별 상승, 하락 횟수:")
    for date in sorted(date_count.keys(), reverse=True): # 날짜를 내림차순으로 정렬
        counts = date_count[date]
        print(f"날짜: {date} - 상승: {counts['상승']}, 하락: {counts['하락']}")
        for stock, stock_counts in counts['종목'].items():
            print(f" - 종목: {stock} - 상승: {stock_counts['상승']}, 하락: {stock_counts['하락']}")
        print("\n")
    