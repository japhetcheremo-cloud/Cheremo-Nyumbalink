
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
import traceback

def diag_view(request):
    import os
    info = {
        'DATABASE_URL_SET': bool(os.environ.get('DATABASE_URL')),
        'DATABASE_URL_PREFIX': os.environ.get('DATABASE_URL', '')[:25],
        'IS_VERCEL': getattr(settings, 'IS_VERCEL', None),
        'DB_ENGINE': settings.DATABASES['default']['ENGINE'],
        'DB_NAME': str(settings.DATABASES['default'].get('NAME', '')),
        'DEBUG': settings.DEBUG,
    }
    # Test DB query
    try:
        from properties.models import Property
        cnt = Property.objects.count()
        info['db_query'] = f'OK, property count: {cnt}'
    except Exception as e:
        info['db_error'] = str(e)
        info['db_traceback'] = traceback.format_exc()
    return JsonResponse(info)

urlpatterns = [
    path('__diag__/', diag_view),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('properties/', include('properties.urls')),
    path('chat/', include('chat.urls')),
]

# Serve uploaded media files during local development only.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
