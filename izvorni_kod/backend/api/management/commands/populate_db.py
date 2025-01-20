import os
import random
import time
import uuid
from django.contrib.gis.geos import Point
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum
from api.models import *
from faker import Faker
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from api.models import Location


def get_or_create_genres():
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
    
    genres_list = []
    
    # Create Genre entries if they do not exist:
    for genre in genres:
        obj, created = Genre.objects.get_or_create(name=genre)
        genres_list.append(obj)

    return genres_list


def get_or_create_record_conditions():
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

    conditions_list = []

    # Create GoldmineConditionRecord entries if they do not exist:
    for record_condition in conditions_records:
        obj, created = GoldmineConditionRecord.objects.get_or_create(
            name=record_condition['name'],
            defaults={
                'abbreviation': record_condition['abbreviation'],
                'description': record_condition['description']
            }
        )
        conditions_list.append(obj)

    return conditions_list


def get_or_create_cover_conditions():
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

    conditions_list = []

    # Create GoldmineConditionCover entries if they do not exist:
    for cover_condition in conditions_covers:
        obj, created = GoldmineConditionCover.objects.get_or_create(
            name=cover_condition['name'],
            defaults={
                'abbreviation': cover_condition['abbreviation'],
                'description': cover_condition['description']
            }
        )
        conditions_list.append(obj)

    return conditions_list


def get_or_create_locations():
    geolocator = Nominatim(user_agent='real_location_populator')

    places = [
        "Zagreb, Croatia",
        "New York, USA",
        "London, UK",
        "Berlin, Germany",
        "Paris, France",
        "Rome, Italy"
        "Sydney, Australia",
        "Tokyo, Japan",
        "Toronto, Canada",
    ]

    locations = []

    for place in places:
        city=place.split(',')[0]
        country=place.split(',')[-1].strip()
        
        location = Location.objects.filter(city=city, country=country).first()
        if location:
            locations.append(location)
            continue 

        try:
            location_data = geolocator.geocode(place, addressdetails=True)
            if location_data:
                coordinates = Point(location_data.longitude, location_data.latitude)
                address = location_data.address

                location = Location.objects.create(
                    address=address,
                    city=city,
                    country=country,
                    coordinates=coordinates
                )

                # print(f"Added: {place} ({location.longitude}, {location.latitude})")
                locations.append(location)
            else:
                # print(f"Could not find: {place}")
                pass
            
            time.sleep(1)  # 1 second pause because of OSM request limit

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error with {place}: {str(e)}")

    return locations


def create_users(num_of_users):
    # Create superuser if it doesn't exist in the database
    superuser = User.objects.filter(is_staff=True, is_superuser=True).first()
    if not superuser:
        superuser = User.objects.create_superuser(
                email='admin@admin.com',
                username='admin',
                password='Super123!',
            ) 

    fake = Faker('en_US')

    users_list = []

    for _ in range(num_of_users):
        while True:
            email = fake.unique.email()
            username = fake.unique.user_name()

            duplicate_email_user = User.objects.filter(email=email).first()
            duplicate_username_user = User.objects.filter(username=username).first()
            if not duplicate_email_user and not duplicate_username_user:
                break

        user = User.objects.create(
            email=email,
            username=username,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
        user.set_password('Default123!')
        user.save()
        users_list.append(user)

    return users_list


def create_records(num_of_records,
                   users,
                   genres,
                   conditions_record,
                   conditions_cover,
                   locations):
    fake = Faker('en_US')

    records_list = []

    i = 0
    while i < num_of_records:
        record, created = Record.objects.get_or_create(
            catalog_number=fake.unique.bothify('?????-#####'),
            defaults={
                'artist': fake.name(),
                'album_name': fake.sentence(nb_words=3).rstrip('.'),
                'release_year': random.randint(1950, 2024),
                'genre': random.choice(genres),
                'location': random.choice(locations),
                'additional_description': lorem_ipsum.paragraph(),
                'record_condition': random.choice(conditions_record),
                'cover_condition': random.choice(conditions_cover),
                'user': random.choice(users)
            }
        )
        if created:
            i += 1
            records_list.append(record)

    return records_list


def create_photos(records):
    # Path to the folder where your seed images live
    image_folder = os.path.join(os.path.dirname(__file__), 'dummy_images')
    image_files = os.listdir(image_folder)

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
                f"{uuid.uuid4()}", 
                django_file,
                save=True
            )


def create_wishlists(users):
    fake = Faker('en_US')

    min_wishes_num = 3
    max_wishes_num = 7

    for user in users:
        num_of_wishes = random.randint(min_wishes_num, max_wishes_num)
        i = 0
        while i < num_of_wishes:
            obj, created = Wishlist.objects.get_or_create(
                record_catalog_number=fake.unique.bothify('????????-########'),
                defaults={
                    'user': user
                }
            )
            if created:
                i += 1

                
class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **options):
        genres = get_or_create_genres()
        conditions_record = get_or_create_record_conditions()
        conditions_cover = get_or_create_cover_conditions()

        locations = get_or_create_locations()

        num_of_users = 10
        users = create_users(num_of_users)

        num_of_records = 50
        records = create_records(
            num_of_records=num_of_records,
            users=users,
            genres=genres,
            conditions_record=conditions_record,
            conditions_cover=conditions_cover,
            locations=locations)

        create_photos(records)
        create_wishlists(users)
