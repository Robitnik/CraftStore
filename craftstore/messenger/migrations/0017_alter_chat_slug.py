# Generated by Django 5.1.6 on 2025-03-02 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0016_alter_chat_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='slug',
            field=models.SlugField(default='Xy2zIEziO0PMq6OZOGYeYrDeOe4RPEmfDGCPHB1Mut6bwXhHDAhGwxFSiYfZKDXsXCVjROyITh', max_length=200, unique=True),
        ),
    ]
