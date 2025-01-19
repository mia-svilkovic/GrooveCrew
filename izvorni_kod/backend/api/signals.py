from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Record, Wishlist, Exchange

@receiver(post_save, sender=Exchange)
def notify_users_on_new_exchange(sender, instance, created, **kwargs):
    if created:
        initiator = instance.initiator_user
        receiver = instance.receiver_user

        subject = f"New Exchange Offer from {initiator.username}!"
        message = (
            f"Hi {receiver.first_name},\n\n"
            f"User {initiator.username} has proposed a new exchange offer. "
            f"Check the details of the exchange here: {settings.SITE_URL}/exchanges/{instance.id}/\n\n"
            f"Best regards,\nThe Record Exchange Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[receiver.email],
            fail_silently=False,
        )

@receiver(post_save, sender=Record)
def notify_wishlist_users_on_new_record(sender, instance, created, **kwargs):
    if created:
        # Find all wishlist entries that match the catalog_number of the new record
        wishlist_entries = Wishlist.objects.filter(record_catalog_number=instance.catalog_number)
        
        for entry in wishlist_entries:
            send_mail(
                subject='Record from Your Wishlist is available!',
                message=(
                    f'Hello {entry.user.first_name},\
                    \nThe record with catalog number "{instance.catalog_number}" ({instance.artist} - {instance.album_name}) from your wishlist has just been added to the system!\
                    \nYou can check it out here: {settings.SITE_URL}/records/{instance.id}/'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[entry.user.email],
                fail_silently=False,
            )
