from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

from api.views import custom_admin_logout

def debug_media(request, path):
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    exists = os.path.exists(full_path)
    media_root = str(settings.MEDIA_ROOT)
    files_in_dir = os.listdir(os.path.dirname(full_path)) if exists else []
    
    return HttpResponse(
        f"Looking for: {full_path}\n"
        f"File exists: {exists}\n"
        f"MEDIA_ROOT: {media_root}\n"
        f"Files in directory: {files_in_dir}"
    )

urlpatterns = [
    path('admin/logout/', custom_admin_logout, name='admin-logout'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('debug-media/<path:path>', debug_media),  # Dodajte ovu liniju
]

if not settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', debug_media),  # Privremeno zamijenite standardno posluživanje s debug viewom
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)