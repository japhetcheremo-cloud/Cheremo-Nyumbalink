
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.core.management import call_command
import io
import traceback

def migrate_view(request):
    out = io.StringIO()
    err = io.StringIO()
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Query applied migrations
            cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY applied DESC")
            rows = cursor.fetchall()
            migrations_applied = [{'app': r[0], 'name': r[1], 'applied': str(r[2])} for r in rows]

            # If admin.0001_initial was applied without users.0001_initial, clean django_migrations
            # or fake/run correctly
            action = request.GET.get('action', 'inspect')
            if action == 'clean_migrations':
                cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
                cursor.execute("GRANT ALL ON SCHEMA public TO public;")
                call_command('migrate', interactive=False, stdout=out, stderr=err)
                
                # Load seeded data if available
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    call_command('loaddata', 'seed_data.json', stdout=out, stderr=err)
                except Exception as load_err:
                    err.write(f"Loaddata warning: {load_err}\n")

                cheremo_user = User.objects.filter(username='cheremo').first()
                if not cheremo_user:
                    cheremo_user = User.objects.create_superuser('cheremo', 'cheremo@gmail.com', 'Japhet@2006')
                    cheremo_user.role = 'landlord'
                    cheremo_user.save()
                else:
                    cheremo_user.set_password('Japhet@2006')
                    cheremo_user.is_superuser = True
                    cheremo_user.is_staff = True
                    cheremo_user.role = 'landlord'
                    cheremo_user.save()

                return JsonResponse({
                    'status': 'success',
                    'action': 're-created schema, migrated and seeded successfully',
                    'cheremo_user_id': cheremo_user.id,
                    'stdout': out.getvalue(),
                    'stderr': err.getvalue(),
                })

            return JsonResponse({
                'status': 'inspected',
                'applied_count': len(migrations_applied),
                'migrations': migrations_applied[:20],
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
