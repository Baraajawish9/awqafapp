from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screen', '0025_screensettings_public_screen_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='preferred_rooms',
            field=models.TextField(blank=True, null=True),
        ),
    ]
