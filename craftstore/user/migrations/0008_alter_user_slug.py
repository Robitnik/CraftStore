# Generated by Django 5.1.1 on 2024-11-23 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_usergoods_goods'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
