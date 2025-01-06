import time
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from io import StringIO
import csv
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import xml.etree.ElementTree as ET

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

def load_config(file_path):
    tree = ET.parse(file_path)  # XML 파일 파싱
    root = tree.getroot()

    # 필요한 데이터 추출
    email = root.find("./api/email").text
    pw = root.find("./api/pw").text

    return email, pw

# 메일 전송 함수
def send_email(subject, body, recipient_email):

    email, pw = load_config("./API_Key/mail_key.xml")
    sender_email = email  # 발신자 이메일
    sender_password = pw  # 발신자 이메일 비밀번호 또는 앱 비밀번호 (Gmail 2단계 인증 시 앱 비밀번호 사용)

    try:
        # SMTP 서버 설정
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # TLS 보안 활성화
            server.login(sender_email, sender_password)  # 로그인

            # 이메일 구성
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject

            # 본문 추가
            msg.attach(MIMEText(body, "html"))

            # 이메일 전송
            server.send_message(msg)
            print("메일이 성공적으로 전송되었습니다.")
    except Exception as e:
        print(f"메일 전송 중 오류 발생: {e}")

# 실행
if __name__ == '__main__':
    start_time = time.time()  # 실행 시작 시간 기록

    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    print(f"실행 시간 : {formatted_time} / 분석중...")

    output = fetch_and_process_data(ticker_list)

    # 초단기예측, 단기예측, 전환예측별 상승/하락 횟수 계산
    category_count = defaultdict(lambda: {'상승': 0, '하락': 0})

    # 날짜별 및 종목별 상승, 하락 횟수 계산
    date_count = defaultdict(lambda: {'상승': 0, '하락': 0, '종목': defaultdict(lambda: {'상승': 0, '하락': 0, 'ticker': None})})

    for record in output:
        date = record["날짜"]
        stock = record["종목명"]
        ticker = record["종목코드"]
        for key in ['초단기예측', '단기예측', '전환예측']:
            if record[key] == '상승':
                category_count[key]['상승'] += 1
                date_count[date]['상승'] += 1
                date_count[date]['종목'][stock]['상승'] += 1
                date_count[date]['종목'][stock]['ticker'] = ticker
            elif record[key] == '하락':
                category_count[key]['하락'] += 1
                date_count[date]['하락'] += 1
                date_count[date]['종목'][stock]['하락'] += 1
                date_count[date]['종목'][stock]['ticker'] = ticker

    # 결과 출력
    end_time = time.time()  # 실행 끝 시간 기록
    execution_time = end_time - start_time  # 실행 시간 계산

    output_text = f"<html><body><div>분석 시간 : {formatted_time} (Execution time: {execution_time:.2f} seconds)</div>"
    print(f"\nExecution time: {execution_time:.2f} seconds")  # 실행 시간 출력
    print("예측별 상승, 하락 횟수:")
    for category, counts in category_count.items():
        print(f"{category}: 상승: {counts['상승']}, 하락: {counts['하락']}")

    output_text += "<br><div>최근 3일 기준 종목별 상승, 하락 신호</div><br>"
    output_text += "<div style='display: flex; gap: 10px;'>"
    print("\n최근 3일 기준 종목별 상승, 하락 신호")
    for date in sorted(date_count.keys(), reverse=True): # 날짜를 내림차순으로 정렬
        counts = date_count[date]
        formatted_date = date.strftime("%Y-%m-%d")  
        print(f"날짜: {formatted_date} - 상승: {counts['상승']}, 하락: {counts['하락']}")
        output_text += "<div style='border: 1px solid #ddd; border-radius: 5px; padding: 5px; font-size: 14px;'>"
        output_text += f"<div style='text-align: center;'>날짜: {formatted_date} - 상승: {counts['상승']}, 하락: {counts['하락']}</div><ul style='padding: 20px; list-style: none;'>"
        
        # 종목 데이터를 상승 횟수를 기준으로 내림차순 정렬
        sorted_stocks = sorted(counts['종목'].items(), key=lambda x: x[1]['상승'], reverse=True)

        for stock, stock_counts in sorted_stocks:
            print(f" - 종목: {stock} - 상승: {stock_counts['상승']}, 하락: {stock_counts['하락']}")
            # 네이버 금융 링크 생성
            ticker = stock_counts['ticker']
            stock_link = f"https://finance.naver.com/item/main.nhn?code={ticker}"
            # HTML 링크 추가
            stock_with_link = f'<a href="{stock_link}" target="_blank">{stock}</a>'
            output_text += f"<li>{stock_with_link} - 상승: {stock_counts['상승']}, 하락: {stock_counts['하락']}</li>"
        print("\n")
        output_text += "</ul></div>"
    output_text +="</div></body></html>"

    # 메일 전송
    recipient_email = "ljh1032112@gmail.com"  # 수신자 이메일
    subject = f"주식 분석 결과 - {formatted_time}"
    send_email(subject, output_text, recipient_email)
