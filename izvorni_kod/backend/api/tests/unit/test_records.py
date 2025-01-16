from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point
from ...models import *


class RecordViewTests(APITestCase):
    def setUp(self):
        """
        Setup runs before each test method.
        Creates necessary users and related objects for testing Record operations.
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

        # Create test genre
        self.genre = Genre.objects.create(name='Rock')

        # Create test location
        self.location = Location.objects.create(
            address='Test Street 123',
            city='Test City',
            country='Test Country',
            coordinates=Point(15.9819, 45.8150)  # Example coordinates for Zagreb
        )

        # Create test conditions
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

        # Create a test record
        self.record = Record.objects.create(
            catalog_number='TEST001',
            artist='Test Artist',
            album_name='Test Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.user,
            additional_description='Test description'
        )

        # Define URLs
        self.list_url = reverse('api:record-list')
        self.create_url = reverse('api:record-add')
        self.detail_url = reverse('api:record-detail', args=[self.record.id])
        self.update_url = reverse('api:record-update', args=[self.record.id])
        self.delete_url = reverse('api:record-delete', args=[self.record.id])

        # Define valid payload for record creation/update
        self.valid_payload = {
            'catalog_number': 'TEST002',
            'artist': 'New Artist',
            'album_name': 'New Album',
            'release_year': 2021,
            'genre_id': self.genre.id,
            'record_condition_id': self.record_condition.id,
            'cover_condition_id': self.cover_condition.id,
            'additional_description': 'New description',
            'location_add': {
                'coordinates': {
                    'latitude': 45.8150,
                    'longitude': 15.9819
                }
            }
        }

    def test_create_record_success(self):
        """
        Test creating a new record with valid data
        """
        # Login user
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.create_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 2)  # Initial record + new one
        self.assertEqual(response.data['artist'], 'New Artist')
        self.assertEqual(response.data['album_name'], 'New Album')
        self.assertEqual(response.data['user']['email'], self.user.email)

    def test_create_record_unauthorized(self):
        """
        Test creating a record without authentication
        """
        response = self.client.post(self.create_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Record.objects.count(), 1)  # Only initial record exists

    def test_get_record_list(self):
        """
        Test retrieving list of records
        """
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['catalog_number'], 'TEST001')

    def test_get_record_detail(self):
        """
        Test retrieving a single record
        """
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['catalog_number'], 'TEST001')
        self.assertEqual(response.data['artist'], 'Test Artist')

    def test_update_record_success(self):
        """
        Test updating a record by its owner
        """
        self.client.force_authenticate(user=self.user)
        
        update_data = self.valid_payload.copy()
        update_data['catalog_number'] = 'UPDATED001'
        
        response = self.client.put(self.update_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['catalog_number'], 'UPDATED001')
        self.assertEqual(response.data['artist'], 'New Artist')

    def test_update_record_unauthorized(self):
        """
        Test updating a record by non-owner
        """
        self.client.force_authenticate(user=self.another_user)
        
        update_data = self.valid_payload.copy()
        update_data['catalog_number'] = 'UPDATED001'
        
        response = self.client.put(self.update_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Verify record wasn't updated
        self.record.refresh_from_db()
        self.assertEqual(self.record.catalog_number, 'TEST001')

    def test_delete_record_success(self):
        """
        Test deleting a record by its owner
        """
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(self.delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Record.objects.count(), 0)

    def test_delete_record_unauthorized(self):
        """
        Test deleting a record by non-owner
        """
        self.client.force_authenticate(user=self.another_user)
        
        response = self.client.delete(self.delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Record.objects.count(), 1)  # Record still exists
