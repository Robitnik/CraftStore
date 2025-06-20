# Generated by Django 5.1.1 on 2024-11-22 09:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdn', '0001_initial'),
        ('store', '0002_remove_store_goods_goods_store'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='path',
        ),
        migrations.AddField(
            model_name='gallery',
            name='img',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_gallery_image', to='cdn.image'),
        ),
        migrations.AddField(
            model_name='goods',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='store',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='store', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='goods',
            name='poster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_image', to='cdn.image'),
        ),
        migrations.AlterField(
            model_name='store',
            name='avatar',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='store_image', to='cdn.image'),
        ),
        migrations.AlterField(
            model_name='store',
            name='slug',
            field=models.SlugField(max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='store',
            name='social_links',
            field=models.ManyToManyField(null=True, related_name='store', to='store.usersocialmedia'),
        ),
    ]
