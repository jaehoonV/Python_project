# stock_chart/urls.py

from django.urls import path
from . import views  # views.py 파일에서 view 함수들을 가져옵니다
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),  # 기본 페이지로 index 뷰를 연결
    path('autocomplete/', views.autocomplete_tickers, name='autocomplete_tickers'),
    path('generate-chart/', views.generate_chart_image, name='generate_chart_image'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
