# Generated by Django 4.2.5 on 2023-09-27 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_uploadedimage_delete_uploadimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedimage',
            name='image',
            field=models.ImageField(blank=True, upload_to='uploads/'),
        ),
    ]
