# Generated by Django 5.2.1 on 2025-05-27 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boxes', '0002_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='product_images/'),
        ),
    ]
