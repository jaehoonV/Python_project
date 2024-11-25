# stock_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock_chart.urls')),  # stock_chart 앱의 URL을 포함
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
