from django.conf import settings
from django.db import models


class Message(models.Model):
    # Every message — whether from the customer or an admin reply — is
    # tied to the customer it belongs to, so a thread is just "all
    # messages for this user, in order."
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    body = models.TextField()
    sender_is_admin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        who = 'Admin' if self.sender_is_admin else self.user.email
        preview = self.body[:40]
        return f'{who}: {preview}'