# stock_chart/views.py
# 실행 python manage.py runserver

import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 대신 이미지로 차트를 렌더링할 수 있게 설정
from django.shortcuts import render
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta
import io
import base64
from django.http import HttpResponse
import matplotlib.dates as mdates
import csv
from django.http import JsonResponse
from django.shortcuts import render
import os
from django.conf import settings

# 티커 목록 가져오기
def get_ticker_list():
    ticker_list = []
    with open('sp500_companies.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ticker_list.append({'symbol': row['Symbol'], 'name': row['Security']})
    return ticker_list

# 자동완성 기능을 처리하는 뷰
def autocomplete_tickers(request):
    query = request.GET.get('q', '')
    ticker_list = get_ticker_list()

    # 입력한 검색어와 일치하는 티커 필터링
    filtered_tickers = [ticker for ticker in ticker_list if query.lower() in ticker['symbol'].lower()]

    # JSON 형식으로 필터링된 결과 반환
    return JsonResponse(filtered_tickers, safe=False)

# 주식 데이터 가져오는 함수
def get_stock_data(selected_ticker, period_days):
    extended_period_days = period_days + 360  # 이동평균선 계산을 위해 120일을 추가
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=extended_period_days)).strftime('%Y-%m-%d')

    stock = yf.Ticker(selected_ticker)
    data = stock.history(start=start_date, end=end_date)
    
    if data.empty:
        return None

    # 이동평균선 및 볼린저 밴드 계산
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA60'] = data['Close'].rolling(window=60).mean()
    data['MA120'] = data['Close'].rolling(window=120).mean()
    data['BB_upper'] = data['MA20'] + (data['Close'].rolling(window=20).std() * 2)
    data['BB_lower'] = data['MA20'] - (data['Close'].rolling(window=20).std() * 2)
    # 기준선 (26일 기준 고가, 저가의 평균) 계산
    data['Baseline'] = (data['High'].rolling(window=26).max() + data['Low'].rolling(window=26).min()) / 2
    # 전환선 (9일 기준 고가, 저가의 평균) 계산
    data['ConversionLine'] = (data['High'].rolling(window=9).max() + data['Low'].rolling(window=9).min()) / 2

    return data

# 차트 생성 함수
def plot_stock_chart(selected_ticker, data, period_days, period_months, show_ma5, show_ma20, show_ma60, show_ma120, show_baseline, show_conversionLine, show_bb, show_volume):
    # 실제로 표시할 기간
    display_data = data.tail(period_days)

    # 5, 20, 60, 120 이동평균선, 기준선, 전환선, 볼린저 밴드 추가
    apds = []
    if show_ma5:
        apds.append(mpf.make_addplot(display_data['MA5'], color='blue', label='MA5 (5-day Moving Avg)'))
    if show_ma20:
        apds.append(mpf.make_addplot(display_data['MA20'], color='orange', label='MA20 (20-day Moving Avg)'))
    if show_ma60:
        apds.append(mpf.make_addplot(display_data['MA60'], color='green', label='MA60 (60-day Moving Avg)'))
    if show_ma120:
        apds.append(mpf.make_addplot(display_data['MA120'], color='red', label='MA120 (120-day Moving Avg)'))
    if show_baseline: # 기준선
        apds.append(mpf.make_addplot(display_data['Baseline'], color='cyan', linestyle='--', label='Baseline (26-day Avg)'))
    if show_conversionLine: # 전환선
        apds.append(mpf.make_addplot(display_data['ConversionLine'], color='magenta', linestyle='--', label='ConversionLine (9-day Avg)'))
    if show_bb:
        apds.append(mpf.make_addplot(display_data['BB_upper'], color='purple', label='Bollinger Upper Band'))
        apds.append(mpf.make_addplot(display_data['BB_lower'], color='purple', label='Bollinger Lower Band'))
    if show_volume: # 거래량
        apds.append(mpf.make_addplot(display_data['Volume'], type='bar', color='grey', alpha=0.2, ylabel="Volume"))

    # 차트 생성
    fig, axes = mpf.plot(display_data , type='candle', style='charles',
                         title=f"{selected_ticker} Stock Prices ({period_months} Months)", ylabel="Price (USD)", addplot=apds, returnfig=True, figsize=(16, 8))

    # 범례 추가
    axes[0].legend(loc='upper left', bbox_to_anchor=(-0.25, 1), fontsize=9)

    plt.xticks(rotation=65)  # 날짜가 겹치지 않도록 회전시킬 수 있습니다.

    # 이미지를 HTML에 삽입할 수 있도록 변환
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_str = base64.b64encode(img_buf.read()).decode('utf-8')
    return img_str

# 기본 페이지
def index(request):
    selected_ticker = request.GET.get("ticker", "AAPL")  # 기본 티커는 AAPL
    selected_ticker_name = request.GET.get("ticker_name", "Apple Inc.")  # 기본 티커는 AAPL
    context = {
        'selected_ticker': selected_ticker,
        'selected_ticker_name': selected_ticker_name,
    }
    return render(request, 'index.html', context)  # 기본 페이지로 index.html 렌더링

# 차트 이미지 생성
def generate_chart_image(request):
    selected_ticker = request.GET.get("ticker", "AAPL")
    period_days = int(request.GET.get('period', 130))
    show_ma5 = request.GET.get('show_ma5') == 'true'
    show_ma20 = request.GET.get('show_ma20') == 'true'
    show_ma60 = request.GET.get('show_ma60') == 'true'
    show_ma120 = request.GET.get('show_ma120') == 'true'
    show_baseline = request.GET.get('show_baseline') == 'true'
    show_conversionLine = request.GET.get('show_conversionLine') == 'true'
    show_bb = request.GET.get('show_bb') == 'true'
    show_volume = request.GET.get('show_volume') == 'true'

    data = get_stock_data(selected_ticker, period_days)

    if data is None:
        return JsonResponse({'error': f"No data available for ticker {selected_ticker}"}, status=400)

    # 차트 데이터 준비
    data_candles = data[['Open', 'High', 'Low', 'Close', 'Volume', 'MA5', 'MA20', 'MA60', 'MA120', 'Baseline', 'ConversionLine', 'BB_upper', 'BB_lower']]

    period_months = 24
    # period_days를 월로 변환
    if period_days == 260: 
        period_months = 12
    elif period_days == 130:
        period_months = 6

    # 차트 이미지 생성
    img_str = plot_stock_chart(selected_ticker, data_candles, period_days, period_months, show_ma5, show_ma20, show_ma60, show_ma120, show_baseline, show_conversionLine, show_bb, show_volume)

    # Base64 인코딩된 이미지 데이터 반환
    return JsonResponse({'chart_img': img_str})
