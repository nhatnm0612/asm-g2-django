# Generated by Django 4.0.10 on 2024-08-03 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='unit',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
    ]