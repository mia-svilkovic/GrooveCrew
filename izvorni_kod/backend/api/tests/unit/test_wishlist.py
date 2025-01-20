from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point
from api.models import *


class WishlistViewTests(APITestCase):
    def setUp(self):
        """
        Setup runs before each test method.
        Creates necessary test users, records and wishlist items.
        """
        # Create test users
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        self.another_user = User.objects.create_user(
            email='another@example.com',
            username='anotheruser',
            password='AnotherPass123!',
            first_name='Another',
            last_name='User'
        )

        # Create required related objects for records
        self.genre = Genre.objects.create(name='Rock')
        self.location = Location.objects.create(
            address='Test Street 123',
            city='Test City',
            country='Test Country',
            coordinates=Point(15.9819, 45.8150)
        )
        self.record_condition = GoldmineConditionRecord.objects.create(
            name='Mint',
            abbreviation='M',
            description='Perfect condition'
        )
        self.cover_condition = GoldmineConditionCover.objects.create(
            name='Mint',
            abbreviation='M',
            description='Perfect condition'
        )

        # Create a test record that matches wishlist catalog number
        self.record = Record.objects.create(
            catalog_number='TEST001',
            artist='Test Artist',
            album_name='Test Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.another_user,
            additional_description='Test description'
        )

        # Create a test wishlist item
        self.wishlist_item = Wishlist.objects.create(
            user=self.user,
            record_catalog_number='TEST001'
        )

        # Define URLs
        self.list_url = reverse('api:wishlist-list')
        self.create_url = reverse('api:wishlist-add')
        self.delete_url = reverse('api:wishlist-delete', args=[self.wishlist_item.id])

        # Define valid payload for wishlist creation
        self.valid_payload = {
            'record_catalog_number': 'TEST002'
        }

    def test_get_wishlist_authenticated(self):
        """
        Test retrieving wishlist items for authenticated user
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['record_catalog_number'], 'TEST001')
        # Verify matching records are included
        self.assertEqual(len(response.data[0]['matching_records']), 1)
        self.assertEqual(response.data[0]['matching_records'][0]['catalog_number'], 'TEST001')

    def test_get_wishlist_unauthenticated(self):
        """
        Test retrieving wishlist items without authentication
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_wishlist_item_success(self):
        """
        Test creating a new wishlist item with valid data
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wishlist.objects.count(), 2)  # Initial item + new one
        self.assertEqual(response.data['record_catalog_number'], 'TEST002')

    def test_create_wishlist_item_duplicate(self):
        """
        Test creating a wishlist item with already existing catalog number
        """
        self.client.force_authenticate(user=self.user)
        duplicate_payload = {
            'record_catalog_number': 'TEST001'  # Already exists in user's wishlist
        }
        
        response = self.client.post(self.create_url, duplicate_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Wishlist.objects.count(), 1)  # No new item created
        self.assertIn('message', response.data)

    def test_create_wishlist_item_unauthenticated(self):
        """
        Test creating a wishlist item without authentication
        """
        response = self.client.post(self.create_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Wishlist.objects.count(), 1)  # No new item created

    def test_delete_wishlist_item_success(self):
        """
        Test deleting a wishlist item by its owner
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Wishlist.objects.count(), 0)

    def test_delete_wishlist_item_unauthorized(self):
        """
        Test deleting a wishlist item by non-owner
        """
        self.client.force_authenticate(user=self.another_user)
        response = self.client.delete(self.delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Wishlist.objects.count(), 1)  # Item still exists

    def test_delete_wishlist_item_unauthenticated(self):
        """
        Test deleting a wishlist item without authentication
        """
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Wishlist.objects.count(), 1)  # Item still exists

    def test_matching_records_functionality(self):
        """
        Test the matching_records functionality by creating multiple matching records
        """
        self.client.force_authenticate(user=self.user)
        
        # Create another matching record
        Record.objects.create(
            catalog_number='TEST001',  # Same as wishlist item
            artist='Another Artist',
            album_name='Another Album',
            release_year=2021,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.another_user,
            additional_description='Another description'
        )
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify both matching records are included
        self.assertEqual(len(response.data[0]['matching_records']), 2)
        # Verify different artists are present
        artists = {record['artist'] for record in response.data[0]['matching_records']}
        self.assertEqual(artists, {'Test Artist', 'Another Artist'})
