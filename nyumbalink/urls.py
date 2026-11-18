
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.core.management import call_command
import io
import traceback

def migrate_view(request):
    # Only allow migration trigger
    out = io.StringIO()
    err = io.StringIO()
    try:
        call_command('migrate', interactive=False, stdout=out, stderr=err)
        return JsonResponse({
            'status': 'success',
            'stdout': out.getvalue(),
            'stderr': err.getvalue(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'stdout': out.getvalue(),
            'stderr': err.getvalue(),
        }, status=500)

urlpatterns = [
    path('__migrate__/', migrate_view),
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
