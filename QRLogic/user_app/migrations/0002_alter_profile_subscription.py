# Generated by Django 5.1.5 on 2025-02-19 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='subscription',
            field=models.CharField(max_length=255),
        ),
    ]
