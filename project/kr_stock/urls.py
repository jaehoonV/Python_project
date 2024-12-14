# kr_stock/urls.py

from django.urls import path
from . import views  # views.py 파일에서 view 함수들을 가져옵니다
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('kr_stock/', views.kr_stock, name='kr_stock'), 
    path('krStockSearch/', views.krStockSearch, name='krStockSearch'), 
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
