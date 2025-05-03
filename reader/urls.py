from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import photo_capture_view, upload_image, edit_data, save_document_data, success_view, error_view
	
urlpatterns = [
    path('', photo_capture_view, name='photo_capture'),
    path('upload/', upload_image, name='upload_image'),
    path('edit/', edit_data, name='edit_data'),
    path('save/', save_document_data, name='save_document_data'),
    path('success/', success_view, name='success'),
    path('error/', error_view, name='error'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)