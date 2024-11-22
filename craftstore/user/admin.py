from django.contrib import admin
from .models import User, Group, UserGoods, ValidatedEmails, MailCode

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone_number', 'user_gender', 'address', 'slug')
    search_fields = ('username', 'email', 'phone_number', 'address')
    list_filter = ('user_gender',)
    ordering = ('username',)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class UserGoodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'goods', 'date')
    search_fields = ('goods__title',)
    ordering = ('-date',)


class ValidatedEmailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'status', 'date', 'code')
    search_fields = ('email', 'code')
    list_filter = ('status',)
    ordering = ('-date',)


class MailCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'date_pub', 'date_updated')
    search_fields = ('user__username', 'code')
    ordering = ('-date_pub',)


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(UserGoods, UserGoodsAdmin)
admin.site.register(ValidatedEmails, ValidatedEmailsAdmin)
admin.site.register(MailCode, MailCodeAdmin)