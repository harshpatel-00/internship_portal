# Generated by Django 4.2.22 on 2025-06-16 14:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Internship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=100)),
                ('duration', models.CharField(max_length=100)),
                ('stipend', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('posted_at', models.DateTimeField(auto_now_add=True)),
                ('posted_by', models.ForeignKey(limit_choices_to={'role': 'recruiter'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
