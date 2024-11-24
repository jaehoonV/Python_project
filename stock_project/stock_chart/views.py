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


# 주식 데이터 가져오는 함수
def get_stock_data(ticker, period_days):
    extended_period_days = period_days + 360  # 이동평균선 계산을 위해 120일을 추가
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=extended_period_days)).strftime('%Y-%m-%d')

    stock = yf.Ticker(ticker)
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

    return data

# 차트 생성 함수
def plot_stock_chart(ticker, data, period_days, period_months):
    # 실제로 표시할 기간
    display_data = data.tail(period_days)

    # 이동평균선 및 볼린저 밴드 추가
    apds = [
        mpf.make_addplot(display_data ['MA5'], color='blue'),
        mpf.make_addplot(display_data ['MA20'], color='orange'),
        mpf.make_addplot(display_data ['MA60'], color='green'),
        mpf.make_addplot(display_data ['MA120'], color='red'),
        mpf.make_addplot(display_data ['BB_upper'], color='purple'),
        mpf.make_addplot(display_data ['BB_lower'], color='purple')
    ]

    # 차트 생성
    fig, axes = mpf.plot(display_data , type='candle', style='charles',
                         title=f"{ticker} Stock Prices ({period_months} Months)", ylabel="Price (USD)",
                         ylabel_lower="Volume", volume=True, addplot=apds, returnfig=True, figsize=(13, 7))

    plt.xticks(rotation=65)  # 날짜가 겹치지 않도록 회전시킬 수 있습니다.

    # 이미지를 HTML에 삽입할 수 있도록 변환
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_str = base64.b64encode(img_buf.read()).decode('utf-8')
    return img_str

# 기본 페이지
def index(request):
    return render(request, 'index.html')  # 기본 페이지로 index.html 렌더링

# 차트 페이지
def chart(request):
    ticker = "AAPL"  # 주식 티커
    period_days = int(request.GET.get('period', 520))  # 기간은 URL 파라미터로 받아옴, 기본값 2년
    data = get_stock_data(ticker, period_days)

    if data is None:
        return HttpResponse("No data available for the selected ticker and period.")

    # 차트 데이터 준비
    data_candles = data[['Open', 'High', 'Low', 'Close', 'Volume', 'MA5', 'MA20', 'MA60', 'MA120', 'BB_upper', 'BB_lower']]
    
    period_months = 24
    # period_days를 월로 변환
    if period_days == 260: 
        period_months = 12
    elif period_days == 130:
        period_months = 6
    
    img_str = plot_stock_chart(ticker, data_candles, period_days, period_months)
    
    return render(request, 'index.html', {'chart_img': img_str, 'period': period_months})  # 차트를 index.html에 전달
