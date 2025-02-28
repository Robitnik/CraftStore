from django.contrib import admin
from django.contrib import admin


from .models import (
    Store, Goods, Characteristic, CharacteristicNameType, 
    Category, UserSocialMedia, SocialMedia
)

class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'owner')
    search_fields = ('name', 'slug', 'owner__username')
    ordering = ('name',)


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'store', 'published', 'views_count', 'bought_count', 'author')
    list_filter = ('published', 'store', 'category', 'date_published')
    search_fields = ('title', 'slug', 'store__name')
    ordering = ('-date_published',)




class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_type', 'value')
    search_fields = ('value', 'name_type__name')


class CharacteristicNameTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'date_published')
    search_fields = ('name', 'slug')
    ordering = ('-date_published',)


class UserSocialMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'social', 'link')
    search_fields = ('link', 'social__name')


class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon')
    search_fields = ('name',)


admin.site.register(Store, StoreAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(Characteristic, CharacteristicAdmin)
admin.site.register(CharacteristicNameType, CharacteristicNameTypeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(UserSocialMedia, UserSocialMediaAdmin)
admin.site.register(SocialMedia, SocialMediaAdmin)