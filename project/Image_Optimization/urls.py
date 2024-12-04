# Image_Optimization/urls.py

from django.urls import path
from . import views  # views.py 파일에서 view 함수들을 가져옵니다
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('imageOptimization/', views.image_index, name='image_index'), 
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
