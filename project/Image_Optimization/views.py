# Image_Optimization/views.py
# 실행 python manage.py runserver
from django.shortcuts import render
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse

# 기본 페이지
def image_index(request):
    return render(request, 'image_index.html')

def optimize_image(original_image, q):
    # 이미지 최적화 로직
    try:
        img = PilImage.open(original_image)
        img = img.convert("RGB")  # JPEG 저장을 위해 RGB로 변환
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=q, optimize=True)
        buffer.seek(0)  # 버퍼의 시작 위치로 이동
        return ContentFile(buffer.getvalue())
    except Exception as e:
        print(f"Image optimization failed: {e}")
        raise ValueError("Failed to optimize the image")

def optimize(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)
    
    file_urls = []  # 업로드된 파일의 URL을 저장할 리스트
    files = request.FILES.getlist('files')
    quality = int(request.POST.get('quality', 70))  # 기본값 70
    print(request)
    print(files)

    for file in files:
        original_image = file
        optimized_image = optimize_image(original_image, quality)
        # 최적화된 이미지 저장
        optimized_image_name = f"{file.name}"
        optimized_image_path = default_storage.save(optimized_image_name, optimized_image)
        # 저장된 파일 URL 추가
        file_urls.append(f"{settings.MEDIA_URL}{optimized_image_path}")

    print(file_urls)
    return JsonResponse({'file_urls': file_urls})  # JSON으로 응답