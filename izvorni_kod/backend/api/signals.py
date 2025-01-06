from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Record, Wishlist

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
