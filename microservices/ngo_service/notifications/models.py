from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Notification(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

@receiver(post_save, sender=Notification)
def broadcast_admin_notification(sender, instance, created, **kwargs):
    """
    Signal receiver that broadcasts a real-time notification via WebSockets
    whenever a new Notification object is created by an admin.
    """
    if created:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {
                    "type": "send_notification",
                    "message": instance.title
                }
            )
            print(f"DEBUG: [Channels] Admin notification broadcasted: {instance.title}")
