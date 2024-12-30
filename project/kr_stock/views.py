# kr_stock/views.py
# 실행 python manage.py runserver
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from ta.trend import PSARIndicator

# 기본 페이지
def kr_stock(request):
    return render(request, 'kr_stock.html')

def load_config(file_path):
    tree = ET.parse(file_path)  # XML 파일 파싱
    root = tree.getroot()

    # 필요한 데이터 추출
    app_key = root.find("./api/app_key").text

    return app_key

def krStockSearch(request):
    url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
    type = request.GET.get("type", "S")
    # API KEY 파일 경로 설정
    API_KEY_file_path = os.path.join(settings.BASE_DIR, 'API_KEY', 'apis_key.xml')

    try:
        app_key = load_config(API_KEY_file_path)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    if type == "S": 
        # 오늘 날짜를 시작으로 설정
        current_date = datetime.today()

        while True:
            # 날짜를 YYYYMMDD 형식으로 변환
            formatted_date = current_date.strftime('%Y%m%d')

            # URL 생성
            request_url = (
                f"{url}?serviceKey={app_key}"
                f"&numOfRows=3000"
                f"&pageNo=1"
                f"&resultType=json"
                f"&basDt={formatted_date}"
            )

            print(f"Requesting data for date: {formatted_date}")

            try:
                # API 요청
                response = requests.get(request_url)
                response.raise_for_status()
                data = response.json()

                # totalCount 확인
                total_count = data.get('response', {}).get('body', {}).get('totalCount', 0)

                if total_count > 0:
                    # 데이터가 있을 경우 반환
                    return JsonResponse({"data": data, "date": current_date.strftime('%Y%m%d')})
                else:
                    # 데이터가 없으면 날짜를 하루 전으로 변경
                    current_date -= timedelta(days=1)
            except requests.exceptions.RequestException as e:
                return JsonResponse({"error": f"HTTP Request Error: {str(e)}"}, status=500)
            except Exception as e:
                return JsonResponse({"error": f"Unexpected Error: {str(e)}"}, status=500)
    elif type == "M":
        #monthChartSearch
        beginBasDt = request.GET.get("beginBasDt")
        current_date = datetime.today()
        endBasDt = current_date.strftime('%Y%m%d')
        itemNm = request.GET.get("itemNm")

        # URL 생성
        request_url = (
            f"{url}?serviceKey={app_key}"
            f"&numOfRows=3000"
            f"&pageNo=1"
            f"&resultType=json"
            f"&beginBasDt={beginBasDt}"
            f"&endBasDt={endBasDt}"
            f"&itmsNm={itemNm}"
        )

        # API 요청
        response = requests.get(request_url)
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data)

def popup_chart(request):
    return render(request, 'pop_stock_chart.html')

def krStockSearchPop(request):
    url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
    # API KEY 파일 경로 설정
    API_KEY_file_path = os.path.join(settings.BASE_DIR, 'API_KEY', 'apis_key.xml')

    try:
        app_key = load_config(API_KEY_file_path)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    beginBasDt = request.GET.get("beginBasDt")
    current_date = datetime.today()
    endBasDt = current_date.strftime('%Y%m%d')
    itemNm = request.GET.get("itemNm")

    # URL 생성
    request_url = (
        f"{url}?serviceKey={app_key}"
        f"&numOfRows=3000"
        f"&pageNo=1"
        f"&resultType=json"
        f"&beginBasDt={beginBasDt}"
        f"&endBasDt={endBasDt}"
        f"&itmsNm={itemNm}"
    )

    # API 요청
    response = requests.get(request_url)
    response.raise_for_status()
    data = response.json()
    items = data['response']['body']['items']['item']
    basDt = [format_date_to_datetime(item['basDt']) for item in items][::-1]
    clpr = [item['clpr'] for item in items][::-1]
    mkp = [item['mkp'] for item in items][::-1]
    hipr = [item['hipr'] for item in items][::-1]
    lopr = [item['lopr'] for item in items][::-1]
    trqu = [item['trqu'] for item in items][::-1]
    fltRt = [item['fltRt'] for item in items][::-1]

    clpr_series = pd.Series(clpr, dtype=float)
    hipr_series = pd.Series(hipr, dtype=float)
    lopr_series = pd.Series(lopr, dtype=float)

    # 이동평균 계산
    MA5 = clpr_series.rolling(window=5).mean().fillna(0).round().astype(int)
    MA20 = clpr_series.rolling(window=20).mean().fillna(0).round().astype(int)
    MA60 = clpr_series.rolling(window=60).mean().fillna(0).round().astype(int)
    MA120 = clpr_series.rolling(window=120).mean().fillna(0).round().astype(int)

    # 볼린저 밴드 계산 (표준편차 포함)
    BB_upper = (MA20 + clpr_series.rolling(window=20).std() * 2).fillna(0).round().astype(int)
    BB_lower = (MA20 - clpr_series.rolling(window=20).std() * 2).fillna(0).round().astype(int)

    # 기준선 (26일 기준 고가, 저가의 평균) 계산
    Baseline = ((hipr_series.rolling(window=26).max() + lopr_series.rolling(window=26).min()) / 2).fillna(0).round().astype(int)
    # 전환선 (9일 기준 고가, 저가의 평균) 계산
    ConversionLine = ((hipr_series.rolling(window=9).max() + lopr_series.rolling(window=9).min()) / 2).fillna(0).round().astype(int)

    # Parabolic SAR 계산
    psar = PSARIndicator(high=hipr_series, low=lopr_series, close=clpr_series)
    PSAR = psar.psar().round().astype(int)

    # 골든크로스 계산
    goldenCrossList = []
    for i in range(120, len(MA5)):
        if MA5[i] > MA20[i] and MA5[i - 1] <= MA20[i - 1] and MA5[i - 2] <= MA20[i - 2] and MA20[i] > MA60[i]:
            goldenCrossList.append([basDt[i], int(MA5[i])])
    
    # 데드크로스 계산
    deadCrossList = []
    for i in range(120, len(MA5)):
        if MA5[i] < MA20[i] and MA5[i - 1] >= MA20[i - 1] and MA5[i - 2] >= MA20[i - 2]:
            deadCrossList.append([basDt[i], int(MA5[i])])

    # BC 골든크로스 계산 (전환선이 기준선 돌파)
    BCGoldenCross = []
    for i in range(120, len(Baseline)):
        if ConversionLine[i] > Baseline[i] and ConversionLine[i - 1] <= Baseline[i - 1] and ConversionLine[i - 2] <= Baseline[i - 2]:
            BCGoldenCross.append([basDt[i], int(ConversionLine[i])])

    # BC 데드크로스 계산 (전환선이 기준선 아래로 하락)
    BCDeadCross = []
    for i in range(120, len(Baseline)):
        if ConversionLine[i] < Baseline[i] and ConversionLine[i - 1] >= Baseline[i - 1] and ConversionLine[i - 2] >= Baseline[i - 2]:
            BCDeadCross.append([basDt[i], int(ConversionLine[i])])

    # 이격도 골든크로스, 데드크로스 계산
    disparityGoldenCross = []
    disparityDeadCross = []
    for i in range(120, len(MA5)):
        pre_disparity = (MA5[i - 1] / MA20[i - 1]) * 100; # 전날 5일선 20일선 이격도
        disparity = (MA5[i] / MA20[i]) * 100; #5일선 20일선 이격도
        if disparity > 97 and pre_disparity <= 97:
            disparityGoldenCross.append([basDt[i], int(MA5[i])])

        if disparity < 102 and pre_disparity >= 102:
            disparityDeadCross.append([basDt[i], int(MA5[i])])

    # RSI 계산
    delta = clpr_series.diff()
    gain = delta.where(delta > 0, 0)  # 상승폭
    loss = -delta.where(delta < 0, 0)  # 하락폭

    # 평균 상승/하락폭 계산 (Wilder’s Smoothing)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()

    # RS 및 RSI 계산
    rs = avg_gain / avg_loss
    RSI = round(100 - (100 / (1 + rs)), 2)

    result = {
        "basDt": basDt[120:],
        "clpr": [int(float(v)) for v in clpr[120:]],
        "mkp": [int(float(v)) for v in mkp[120:]],
        "hipr": [int(float(v)) for v in hipr[120:]],
        "lopr": [int(float(v)) for v in lopr[120:]],
        "trqu": [int(float(v)) for v in trqu[120:]],
        "fltRt": [float(v) for v in fltRt[120:]],
        "MA5": MA5[120:].tolist(),
        "MA20": MA20[120:].tolist(),
        "MA60": MA60[120:].tolist(),
        "MA120": MA120[120:].tolist(),
        "BB_upper": BB_upper[120:].tolist(),
        "BB_lower": BB_lower[120:].tolist(),
        "Baseline": Baseline[120:].tolist(),
        "ConversionLine": ConversionLine[120:].tolist(),
        "PSAR": PSAR[120:].tolist(),
        "goldenCrossList": goldenCrossList,
        "deadCrossList": deadCrossList,
        "BCGoldenCross": BCGoldenCross,
        "BCDeadCross": BCDeadCross,
        "disparityGoldenCross": disparityGoldenCross,
        "disparityDeadCross": disparityDeadCross,
        "RSI": RSI[120:].tolist(),
    }

    return JsonResponse(result)

def format_date_to_datetime(dt):
    # Convert to 'YYYY-MM-DD' format
    formatted_date = f"{dt[:4]}-{dt[4:6]}-{dt[6:8]}"
    # Create a datetime object and set time to 0
    return datetime.strptime(formatted_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
