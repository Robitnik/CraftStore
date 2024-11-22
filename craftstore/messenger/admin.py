from django.contrib import admin
from .models import Chat, Massage

class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'date')
    search_fields = ('slug',)
    ordering = ('-date',)
    filter_horizontal = ('members', 'masseges')

class MassageAdmin(admin.ModelAdmin):
    list_display = ('id', 'massege', 'sender', 'read', 'send_date', 'edit_date')
    list_filter = ('read', 'send_date')
    search_fields = ('massege', 'sender__username')
    ordering = ('-send_date',)

admin.site.register(Chat, ChatAdmin)
admin.site.register(Massage, MassageAdmin)
