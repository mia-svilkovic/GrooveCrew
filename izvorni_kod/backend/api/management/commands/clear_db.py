from django.core.management.base import BaseCommand
from api.models import *
                
class Command(BaseCommand):
    help = 'Clear database'

    def handle(self, *args, **options):
        ExchangeRecordRequestedByReceiver.objects.all().delete()
        ExchangeOfferedRecord.objects.all().delete()
        Exchange.objects.all().delete()
        Photo.objects.all().delete()
        Location.objects.all().delete()
        Record.objects.all().delete()
        Wishlist.objects.all().delete()
        Genre.objects.all().delete()
        GoldmineConditionRecord.objects.all().delete()
        GoldmineConditionCover.objects.all().delete()
        User.objects.all().delete()
