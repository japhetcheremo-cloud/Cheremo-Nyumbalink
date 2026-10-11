from django.db import migrations, models
from django.core.files.storage import default_storage

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='verification_document',
            field=models.FileField(blank=True, null=True, upload_to='verification_docs/'),
        ),
    ]
