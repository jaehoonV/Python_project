# stock_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock_chart.urls')),  # stock_chart 앱의 URL을 포함
]
