from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TelegramProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=50, unique=True)),
                ('language', models.CharField(blank=True, choices=[('uz', "O'zbekcha"), ('ru', 'Русский')], max_length=2)),
                ('pending_tracking_code', models.CharField(blank=True, max_length=64)),
            ],
        ),
    ]
