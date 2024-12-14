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
        endBasDt = request.GET.get("endBasDt")
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
