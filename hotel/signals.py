# hotel/signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Customer

@receiver(post_delete, sender=Customer)
def release_room_on_customer_delete(sender, instance, **kwargs):
    if instance.room:
        instance.room.is_available = True
        instance.room.save()