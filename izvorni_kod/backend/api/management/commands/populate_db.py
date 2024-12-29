import os
import random

from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum
from django.core.files import File

from api.models import (
    Genre, GoldmineConditionCover, GoldmineConditionRecord,
    Photo, Record, User, Wishlist
)

from faker import Faker


def create_genres():
    # Genres
    genres = ['Rock',
                'Pop',
                'Electronic / EDM',
                'Hip Hop / Rap',
                'R&B / Soul / Funk',
                'Jazz',
                'Blues',
                'Reggae / Ska / Dub',
                'Latin / World',
                'Country / Folk',
                'Classical',
                'Soundtracks / Scores',
                'Experimental / Avant-Garde',
                'Gospel / Religious',
                'Miscellaneous / Other'
            ]
    
    # Create Genre entries if they do not exist:
    for genre in genres:
        Genre.objects.get_or_create(name=genre)


def create_goldmine_conditions():
    # Standard Goldmine conditions for records:
    conditions_records = [
        {
            'name': 'Mint',
            'abbreviation': 'M',
            'description': 'A perfect record in every way. Unplayed, brand new, and flawless.'
        },
        {
            'name': 'Near Mint',
            'abbreviation': 'NM',
            'description': 'A nearly perfect record. No obvious signs of wear.'
        },
        {
            'name': 'Very Good Plus',
            'abbreviation': 'VG+',
            'description': 'Shows some signs of wear and may have slight scuffs or light scratches.'
        },
        {
            'name': 'Very Good',
            'abbreviation': 'VG',
            'description': 'Noticeable surface noise and light scratches, but still a decent listen.'
        },
        {
            'name': 'Good Plus',
            'abbreviation': 'G+',
            'description': 'Heavier wear with more pronounced scratches and surface noise.'
        },
        {
            'name': 'Good',
            'abbreviation': 'G',
            'description': 'Significant wear, likely with consistent surface noise.'
        },
        {
            'name': 'Fair',
            'abbreviation': 'F',
            'description': 'Likely playable but very noisy with lots of wear. Generally for collection filler.'
        },
        {
            'name': 'Poor',
            'abbreviation': 'P',
            'description': 'Severe damage; may be cracked or unplayable. Collection filler only.'
        },
    ]

    # Create GoldmineConditionRecord entries if they do not exist:
    for record_condition in conditions_records:
        GoldmineConditionRecord.objects.get_or_create(
            name=record_condition['name'],
            defaults={
                'abbreviation': record_condition['abbreviation'],
                'description': record_condition['description']
            }
        )

    # Standard Goldmine conditions for covers (jackets/sleeves):
    conditions_covers = [
        {
            'name': 'Mint',
            'abbreviation': 'M',
            'description': 'Absolutely flawless cover; no creases, folds, or marks.'
        },
        {
            'name': 'Near Mint',
            'abbreviation': 'NM',
            'description': 'Very slight signs of handling or shelf wear, no major imperfections.'
        },
        {
            'name': 'Very Good Plus',
            'abbreviation': 'VG+',
            'description': 'Minor wear on edges/corners, slight ring wear or small creases.'
        },
        {
            'name': 'Very Good',
            'abbreviation': 'VG',
            'description': 'More pronounced wear, small writing, ring wear, or scuffs on the cover.'
        },
        {
            'name': 'Good Plus',
            'abbreviation': 'G+',
            'description': 'Moderate shelf wear, possible splits or tearing, but still generally intact.'
        },
        {
            'name': 'Good',
            'abbreviation': 'G',
            'description': 'Heavy wear, seams may be split, writing or tape might be present.'
        },
        {
            'name': 'Fair',
            'abbreviation': 'F',
            'description': 'Extremely worn. Major splits, tears, or defacement.'
        },
        {
            'name': 'Poor',
            'abbreviation': 'P',
            'description': 'Cover is severely damaged or missing major portions.'
        },
    ]

    # Create GoldmineConditionCover entries if they do not exist:
    for cover_condition in conditions_covers:
        GoldmineConditionCover.objects.get_or_create(
            name=cover_condition['name'],
            defaults={
                'abbreviation': cover_condition['abbreviation'],
                'description': cover_condition['description']
            }
        )


def create_users():
    # Create superuser if it doesn't exist in the database
    superuser = User.objects.filter(is_staff=True, is_superuser=True).first()
    if not superuser:
        superuser = User.objects.create_superuser(
                email='admin@admin.com',
                username='admin',
                password='Super123!',
            ) 

    fake = Faker()

    for _ in range(10):
        user, created = User.objects.get_or_create(
            email = fake.unique.email(),
            defaults={
                'username': fake.user_name,
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
            }
        )
        if created:
            user.set_password('Default123!')
            user.save()


def create_records():
    fake = Faker()

    # Fetch models used in Record's foreign key fields
    users = User.objects.exclude(username='admin')
    genres = Genre.objects.all()
    goldmine_record = GoldmineConditionRecord.objects.all()
    goldmine_cover = GoldmineConditionCover.objects.all()

    # Records
    for _ in range(50):
        Record.objects.get_or_create(
            catalog_number=fake.unique.bothify('?????-#####'),
            defaults={
                'artist': fake.name(),
                'album_name': " ".join(fake.words(nb=random.randint(1, 5))),
                'release_year': random.randint(1950, 2024),
                'genre': random.choice(genres),
                'location': fake.city(),
                'available_for_exchange': fake.boolean(chance_of_getting_true=75),
                'additional_description': lorem_ipsum.paragraph(),
                'record_condition': random.choice(goldmine_record),
                'cover_condition': random.choice(goldmine_cover),
                'user': random.choice(users)
            }
        )


def create_photos(command: "Command"):
    # Path to the folder where your seed images live
    image_folder = os.path.join(os.path.dirname(__file__), 'dummy_images')
    image_files = os.listdir(image_folder)

    records = Record.objects.all()

    for record in records:
        # Choose a random image from the folder
        random_image_name = random.choice(image_files)
        image_path = os.path.join(image_folder, random_image_name)

        with open(image_path, 'rb') as f:
            # Create a Django File object
            django_file = File(f)

            # Create a Photo instance
            photo = Photo(record=record)
            # Save the image to your Photo model’s ImageField
            photo.image.save(
                f"{record.catalog_number}_{random_image_name}", 
                django_file,
                save=True
            )

        # command.stdout.write(command.style.SUCCESS(f"Image {random_image_name} saved for record {record.catalog_number}."))


def create_wishlists():
    fake = Faker()

    users = User.objects.exclude(username='admin')
    for user in users:
        for _ in range(5):
            Wishlist.objects.get_or_create(
                record_catalog_number=fake.unique.bothify('?????-#####'),
                user=user,
            )


class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **options):
        create_users()
        create_genres()
        create_goldmine_conditions()
        create_records()
        create_photos(self)
        create_wishlists()
