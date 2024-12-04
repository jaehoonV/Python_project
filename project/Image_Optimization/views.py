# Image_Optimization/views.py
# 실행 python manage.py runserver
from django.shortcuts import render
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

# 기본 페이지
def image_index(request):
    file_urls = []  # 업로드된 파일의 URL을 저장할 리스트

    if request.method == "POST":
        files = request.FILES.getlist('files')
        quality = int(request.POST.get('quality', 70))  # 기본값 70
        
        for file in files:
            original_image = file
            optimized_image = optimize_image(original_image, quality)
            # 최적화된 이미지 저장
            optimized_image_name = f"{file.name}"
            optimized_image_path = default_storage.save(optimized_image_name, optimized_image)
            # 저장된 파일 URL 추가
            file_urls.append(f"{settings.MEDIA_URL}{optimized_image_path}")

        return render(request, 'image_index.html', {
            'file_urls': file_urls
        })
    
    return render(request, 'image_index.html')

def optimize_image(original_image, q):
    # 이미지 최적화 로직
    img = PilImage.open(original_image)
    img = img.convert("RGB")  # RGB로 변환 (JPEG 저장을 위해)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=q, optimize=True) 
    return ContentFile(buffer.getvalue())