# stock_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock_chart.urls')),  # stock_chart 앱의 URL을 포함
    path('', include('stock_chart_bokeh.urls')),  # stock_chart_bokeh 앱의 URL을 포함
    path('', include('Image_Optimization.urls')),  # Image_Optimization 앱의 URL을 포함
    path('', include('kr_stock.urls')),  # kr_stock 앱의 URL을 포함
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
