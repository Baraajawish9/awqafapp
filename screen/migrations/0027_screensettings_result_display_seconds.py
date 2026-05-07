from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screen', '0026_student_preferred_rooms'),
    ]

    operations = [
        migrations.AddField(
            model_name='screensettings',
            name='result_display_seconds',
            field=models.IntegerField(default=30),
        ),
    ]
