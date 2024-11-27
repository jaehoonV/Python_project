# stock_chart/urls.py

from django.urls import path
from . import views  # views.py 파일에서 view 함수들을 가져옵니다
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('bokeh/', views.bokeh_index, name='bokeh_index'),  # 기본 페이지로 index 뷰를 연결
    path('update_chart/', views.update_chart, name='update_chart'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
