# stock_chart_bokeh/views.py
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
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource, DatetimeTickFormatter, DatetimeTicker, CustomJS
from bokeh.palettes import Spectral11
from bokeh.layouts import gridplot
from ta.trend import PSARIndicator

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

    # Parabolic SAR 계산
    psar = PSARIndicator(high=data['High'], low=data['Low'], close=data['Close'])
    data['PSAR'] = psar.psar()

    # RSI 계산
    data['RSI'] = calculate_rsi(data)

    return data

# 기본 페이지
def bokeh_index(request):
    selected_ticker = request.GET.get("ticker", "AAPL")  # 기본 티커는 AAPL
    selected_ticker_name = request.GET.get("ticker_name", "Apple Inc.")  # 기본 티커는 AAPL
    context = {
        'selected_ticker': selected_ticker,
        'selected_ticker_name': selected_ticker_name,
    }
    return render(request, 'bokeh_index.html', context)  # 기본 페이지로 index.html 렌더링

# Bokeh 차트 생성
def create_bokeh_chart(data, options):
    if 'Date' not in data.columns:
        data = data.reset_index()

    # 타임존 제거
    data['Date'] = data['Date'].dt.tz_localize(None)
    
    source = ColumnDataSource(data)
    
    p = figure(
        x_axis_type="datetime",
        width=1500,
        height=400,
        tools="pan,box_zoom,reset,save"
    )
    
    # 캔들 차트 구현
    inc = source.data['Close'] > source.data['Open']
    dec = source.data['Open'] > source.data['Close']
    p.segment(source.data['Date'], source.data['High'], source.data['Date'], source.data['Low'], color="black")
    p.vbar(source.data['Date'][inc], width=timedelta(days=0.5), top=source.data['Close'][inc], bottom=source.data['Open'][inc], fill_color="#ED3738", line_color="#ED3738")
    p.vbar(source.data['Date'][dec], width=timedelta(days=0.5), top=source.data['Open'][dec], bottom=source.data['Close'][dec], fill_color="#0F81E8", line_color="#0F81E8")

    if options['show_ma5']:
        p.line(source.data['Date'], source.data['MA5'], color="blue", legend_label="5-day MA")
    if options['show_ma20']:
        p.line(source.data['Date'], source.data['MA20'], color="orange", legend_label="20-day MA")
    if options['show_ma60']:
        p.line(source.data['Date'], source.data['MA60'], color="green", legend_label="60-day MA")
    if options['show_ma120']:
        p.line(source.data['Date'], source.data['MA120'], color="red", legend_label="120-day MA")
    if options['show_baseline']: # 기준선
        p.line(source.data['Date'], source.data['Baseline'], color="cyan", legend_label="Baseline")
    if options['show_conversionLine']: # 전환선
        p.line(source.data['Date'], source.data['ConversionLine'], color="magenta", legend_label="ConversionLine")
    if options['show_bb']:
        p.line(source.data['Date'], source.data['BB_upper'], color="yellow", legend_label="Bollinger Upper Band")
        p.line(source.data['Date'], source.data['BB_lower'], color="yellow", legend_label="Bollinger Lower Band")
    if options['show_psar']:
        p.scatter(source.data['Date'], source.data['PSAR'], size=4, color="purple", marker="circle", legend_label="Parabolic SAR")

    # x축 날짜 형식 설정
    p.xaxis.formatter = DatetimeTickFormatter(
        days="%Y-%m-%d",  # "년-월-일" 형식
        months="%Y-%m",   # "년-월" 형식
        years="%Y"        # "년" 형식
    )

    # x축 날짜 간격을 설정하려면 DatetimeTicker 사용
    p.xaxis.ticker = DatetimeTicker(desired_num_ticks=30)  # 날짜 간격을 좁히기
    p.xaxis.major_label_orientation = 0.75  # 레이블 기울기

    p.legend.location = "top_left"
    p.legend.label_text_font_size = "7pt"
    p.legend.padding = 2
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price (USD)"

    # RSI 보조 지표 추가
    p_rsi = figure(
        x_axis_type="datetime",
        width=1500,
        height=200,
        tools="pan,box_zoom,reset,save",
        title="RSI"
    )
    p_rsi.line(source.data['Date'], source.data['RSI'], color="lime", legend_label="RSI")
    p_rsi.line(source.data['Date'], [70] * len(source.data['Date']), color="red", legend_label="Overbought (70)", line_dash="dashed")
    p_rsi.line(source.data['Date'], [30] * len(source.data['Date']), color="blue", legend_label="Oversold (30)", line_dash="dashed")
    p_rsi.legend.location = "top_left"
    p_rsi.legend.label_text_font_size = "7pt"
    p_rsi.legend.padding = 2 
    p_rsi.xaxis.formatter = DatetimeTickFormatter(days="%Y-%m-%d", months="%Y-%m", years="%Y")
    p_rsi.xaxis.ticker = DatetimeTicker(desired_num_ticks=30)
    p_rsi.xaxis.major_label_orientation = 0.75
    p_rsi.xaxis.axis_label = "Date"
    p_rsi.yaxis.axis_label = "RSI"

    # Gridplot으로 메인 차트와 RSI를 결합
    layout = gridplot([[p], [p_rsi]])

    return components(layout)

# RSI 계산 함수
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()  # 종가의 차이 계산
    gain = delta.where(delta > 0, 0)  # 상승폭
    loss = -delta.where(delta < 0, 0)  # 하락폭

    # 평균 상승/하락폭 계산 (Wilder’s Smoothing)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    # RS 및 RSI 계산
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def update_chart(request):
    ticker = request.GET.get("ticker", "AAPL")
    period = int(request.GET.get("period", 130))
    options = {
        "show_ma5": request.GET.get("show_ma5") == "true",
        "show_ma20": request.GET.get("show_ma20") == "true",
        "show_ma60": request.GET.get("show_ma60") == "true",
        "show_ma120": request.GET.get("show_ma120") == "true",
        "show_baseline": request.GET.get('show_baseline') == 'true',
        "show_conversionLine": request.GET.get('show_conversionLine') == 'true',
        "show_bb": request.GET.get('show_bb') == 'true',
        "show_volume": request.GET.get('show_volume') == 'true',
        "show_psar": request.GET.get('show_psar') == 'true'
    }

    data = get_stock_data(ticker, period)
    if data is None:
        return JsonResponse({"error": "No data available for the selected ticker."}, status=400)
    # 실제로 표시할 기간
    display_data = data.tail(period)

    script, div = create_bokeh_chart(display_data, options)
    return JsonResponse({"bokeh_script": script, "bokeh_div": div})