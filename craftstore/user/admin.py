from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Group, ValidatedEmails, MailCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar', 'address', 'phone_number', 'user_gender')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        #(_('Additional info'), {'fields': ('favorites', 'views_history', 'cart', 'slug')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
        }),
    )


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class ValidatedEmailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'status', 'date', 'code')
    search_fields = ('email', 'code')
    list_filter = ('status',)
    ordering = ('-date',)


class MailCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'date_pub', 'date_updated')
    search_fields = ('user__username', 'code')
    ordering = ('-date_pub',)


admin.site.register(Group, GroupAdmin)
admin.site.register(ValidatedEmails, ValidatedEmailsAdmin)
admin.site.register(MailCode, MailCodeAdmin)