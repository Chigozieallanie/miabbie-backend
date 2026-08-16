from rest_framework import generics, permissions
from .models import Message
from .serializers import MessageSerializer


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Customers only ever see their own thread — never anyone else's
        return Message.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Messages sent through this endpoint are always from the customer.
        # Admin replies happen through Django admin instead, which sets
        # sender_is_admin=True directly.
        serializer.save(user=self.request.user, sender_is_admin=False)