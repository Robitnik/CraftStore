from django.contrib import admin
from .models import Cloud, Image

class CloudAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'bucket_name', 'status', 'created_at', 'host_server')
    list_filter = ('status', 'host_server')
    search_fields = ('name', 'bucket_name')
    ordering = ('-created_at', 'id') 


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'cloud', 'url', 'create_at', 'slug', 'author')
    list_filter = ('create_at', 'cloud')  
    search_fields = ('url', 'slug')
    ordering = ('-create_at', 'id')

admin.site.register(Cloud, CloudAdmin)
admin.site.register(Image, ImageAdmin)
