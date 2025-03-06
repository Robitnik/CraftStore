from django.contrib import admin
from .models import Chat, Message

class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'date')
    search_fields = ('slug',)
    ordering = ('-date',)
    filter_horizontal = ('members',)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'sender', 'read', 'send_date', 'edit_date')
    list_filter = ('read', 'send_date')
    search_fields = ('message', 'sender__username')
    ordering = ('-send_date',)

admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
