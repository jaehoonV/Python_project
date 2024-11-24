# stock_chart/urls.py

from django.urls import path
from . import views  # views.py 파일에서 view 함수들을 가져옵니다

urlpatterns = [
    path('', views.index, name='index'),  # 기본 페이지로 index 뷰를 연결
    path('chart/', views.chart, name='chart'),  # 차트 페이지로 chart 뷰를 연결
    path('autocomplete/', views.autocomplete_tickers, name='autocomplete_tickers'),
]
