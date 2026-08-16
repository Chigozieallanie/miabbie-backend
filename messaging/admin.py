from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_body', 'sender_is_admin', 'created_at')
    list_filter = ('sender_is_admin', 'created_at')
    search_fields = ('user__email', 'body')
    ordering = ('-created_at',)

    def short_body(self, obj):
        return obj.body[:60]
    short_body.short_description = 'Message'