from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.gis.geos import Point
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rest_framework import status
from rest_framework.test import APITestCase
from .management.commands.populate_db import populate_db
from .models import *


class RegisterViewTests(APITestCase):
    def setUp(self):
        """
        Setup runs before each test method
        """
        self.register_url = reverse('api:user-register')
        self.valid_payload = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_valid_user(self):
        """
        Test creating a new user with valid payload
        """
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertTrue('tokens' in response.data)
        self.assertTrue('refresh' in response.data['tokens'])
        self.assertTrue('access' in response.data['tokens'])

    def test_create_invalid_user_passwords_dont_match(self):
        """
        Test creating a new user with non-matching passwords
        """
        payload = self.valid_payload.copy()
        payload['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertIn('message', response.data)

    def test_create_invalid_user_email_exists(self):
        """
        Test creating a user with an email that already exists
        """
        # First create a user
        self.client.post(self.register_url, self.valid_payload, format='json')
        
        # Try to create another user with the same email
        payload = self.valid_payload.copy()
        payload['username'] = 'differentuser'
        
        response = self.client.post(self.register_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_create_invalid_user_username_exists(self):
        """
        Test creating a user with a username that already exists
        """
        # First create a user
        self.client.post(self.register_url, self.valid_payload, format='json')
        
        # Try to create another user with the same username
        payload = self.valid_payload.copy()
        payload['email'] = 'different@example.com'
        
        response = self.client.post(self.register_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_create_invalid_user_missing_fields(self):
        """
        Test creating a user with missing required fields
        """
        required_fields = ['email', 'username', 'password1', 'password2', 'first_name', 'last_name']
        
        for field in required_fields:
            payload = self.valid_payload.copy()
            del payload[field]
            
            response = self.client.post(self.register_url, payload, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(User.objects.count(), 0)


class LoginViewTests(APITestCase):
    def setUp(self):
        """
        Setup runs before each test method
        Create a regular user and a staff user for testing
        """
        self.login_url = reverse('api:user-login')
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='regularuser',
            password='RegularPass123!',
            first_name='Regular',
            last_name='User'
        )

        # Create staff user
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            username='staffuser',
            password='StaffPass123!',
            first_name='Staff',
            last_name='User',
            is_staff=True
        )

        # Define valid login payloads
        self.regular_user_payload = {
            'email': 'user@example.com',
            'password': 'RegularPass123!'
        }
        
        self.staff_user_payload = {
            'email': 'staff@example.com',
            'password': 'StaffPass123!'
        }

    def test_login_regular_user_success(self):
        """
        Test successful login for regular user
        Should return tokens but no session cookies
        """
        response = self.client.post(self.login_url, self.regular_user_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('access', response.data['tokens'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.regular_user.email)
        
        # Regular user should not get session cookie
        self.assertNotIn('sessionid', response.cookies)

    def test_login_staff_user_success(self):
        """
        Test successful login for staff user
        Should return tokens and set session cookies
        """
        response = self.client.post(self.login_url, self.staff_user_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('access', response.data['tokens'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.staff_user.email)
        
        # Staff user should get session cookie
        self.assertIn('sessionid', response.cookies)
        
    def test_login_invalid_credentials(self):
        """
        Test login with invalid password
        """
        invalid_payload = self.regular_user_payload.copy()
        invalid_payload['password'] = 'WrongPass123!'
        
        response = self.client.post(self.login_url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(str(response.data['message'][0]), 'Invalid credentials. Please try again.')

    def test_login_inactive_user(self):
        """
        Test login with inactive user account
        Should fail with invalid credentials message
        """
        # Make user inactive
        self.regular_user.is_active = False
        self.regular_user.save()
        
        response = self.client.post(self.login_url, self.regular_user_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(str(response.data['message'][0]), 'Invalid credentials. Please try again.')

    def test_login_missing_fields(self):
        """
        Test login with missing required fields
        """
        # Test missing email
        payload_no_email = {'password': 'RegularPass123!'}
        response = self.client.post(self.login_url, payload_no_email, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test missing password
        payload_no_password = {'email': 'user@example.com'}
        response = self.client.post(self.login_url, payload_no_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """
        Test login with email that doesn't exist in system
        """
        nonexistent_payload = {
            'email': 'nonexistent@example.com',
            'password': 'SomePass123!'
        }
        
        response = self.client.post(self.login_url, nonexistent_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(str(response.data['message'][0]), 'Invalid credentials. Please try again.')


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


class ExchangeCreationTests(APITestCase):
    def setUp(self):
        """
        Setup test cases with necessary users and records.
        Creates two users:
        - initiator_user: who will initiate the exchange
        - receiver_user: who owns the requested record
        """
        # Create test users
        self.initiator_user = User.objects.create_user(
            email='initiator@example.com',
            username='initiator',
            password='InitiatorPass123!',
            first_name='Initiator',
            last_name='User'
        )
        
        self.receiver_user = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='ReceiverPass123!',
            first_name='Receiver',
            last_name='User'
        )

        # Create required related objects
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

        # Create records that will be requested (owned by receiver)
        self.requested_record = Record.objects.create(
            catalog_number='REC001',
            artist='Requested Artist',
            album_name='Requested Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.receiver_user,
            additional_description='Record to be requested'
        )

        # Create records that will be offered (owned by initiator)
        self.offered_record1 = Record.objects.create(
            catalog_number='OFF001',
            artist='Offered Artist 1',
            album_name='Offered Album 1',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user,
            additional_description='First record to offer'
        )

        self.offered_record2 = Record.objects.create(
            catalog_number='OFF002',
            artist='Offered Artist 2',
            album_name='Offered Album 2',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user,
            additional_description='Second record to offer'
        )

        # Define URLs
        self.create_url = reverse('api:exchange-create')

        # Define valid payload for exchange creation
        self.valid_payload = {
            'requested_record_id': self.requested_record.id,
            'offered_records': [
                {'record_id': self.offered_record1.id},
                {'record_id': self.offered_record2.id}
            ]
        }

    def test_create_exchange_success(self):
        """
        Test successful creation of an exchange with valid data
        """
        self.client.force_authenticate(user=self.initiator_user)
        response = self.client.post(self.create_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exchange.objects.count(), 1)
        
        # Verify exchange details
        exchange = Exchange.objects.first()
        self.assertEqual(exchange.initiator_user, self.initiator_user)
        self.assertEqual(exchange.receiver_user, self.receiver_user)
        self.assertEqual(exchange.requested_record, self.requested_record)
        self.assertEqual(exchange.next_user_to_review, self.receiver_user)
        self.assertFalse(exchange.completed)
        
        # Verify offered records
        self.assertEqual(exchange.offered_records.count(), 2)
        offered_record_ids = set(exchange.offered_records.values_list('record_id', flat=True))
        expected_ids = {self.offered_record1.id, self.offered_record2.id}
        self.assertEqual(offered_record_ids, expected_ids)

    def test_create_exchange_no_authentication(self):
        """
        Test exchange creation without authentication
        """
        response = self.client.post(self.create_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Exchange.objects.count(), 0)

    def test_create_exchange_no_offered_records(self):
        """
        Test exchange creation without any offered records
        """
        self.client.force_authenticate(user=self.initiator_user)
        payload = self.valid_payload.copy()
        payload['offered_records'] = []
        
        response = self.client.post(self.create_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Exchange.objects.count(), 0)

    def test_create_exchange_with_unavailable_record(self):
        """
        Test exchange creation with a record that's already part of another exchange
        """
        # First create a valid exchange
        self.client.force_authenticate(user=self.initiator_user)
        self.client.post(self.create_url, self.valid_payload, format='json')
        
        # Try to create another exchange with the same requested record
        response = self.client.post(self.create_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Exchange.objects.count(), 1)

    def test_create_exchange_with_nonexistent_record(self):
        """
        Test exchange creation with non-existent record IDs
        """
        self.client.force_authenticate(user=self.initiator_user)
        payload = self.valid_payload.copy()
        payload['requested_record_id'] = 99999  # Non-existent ID
        
        response = self.client.post(self.create_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Exchange.objects.count(), 0)

    def test_create_exchange_with_own_record(self):
        """
        Test exchange creation where user tries to request their own record
        """
        self.client.force_authenticate(user=self.initiator_user)
        
        # Create a record owned by the initiator
        own_record = Record.objects.create(
            catalog_number='OWN001',
            artist='Own Artist',
            album_name='Own Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )
        
        payload = self.valid_payload.copy()
        payload['requested_record_id'] = own_record.id
        
        response = self.client.post(self.create_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Exchange.objects.count(), 0)


class ExchangeUpdateTests(APITestCase):
    def setUp(self):
        """
        Setup test environment.
        Creates users, records, and an initial exchange for testing updates.
        """
        # Create test users
        self.initiator_user = User.objects.create_user(
            email='initiator@example.com',
            username='initiator',
            password='InitiatorPass123!',
            first_name='Initiator',
            last_name='User'
        )
        
        self.receiver_user = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='ReceiverPass123!',
            first_name='Receiver',
            last_name='User'
        )

        # Create required related objects
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

        # Create requested record (owned by receiver)
        self.requested_record = Record.objects.create(
            catalog_number='REC001',
            artist='Requested Artist',
            album_name='Requested Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.receiver_user
        )

        # Create records owned by initiator
        self.offered_record1 = Record.objects.create(
            catalog_number='OFF001',
            artist='Offered Artist 1',
            album_name='Offered Album 1',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        self.offered_record2 = Record.objects.create(
            catalog_number='OFF002',
            artist='Offered Artist 2',
            album_name='Offered Album 2',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        # Create additional records owned by initiator (for testing add/remove)
        self.additional_record = Record.objects.create(
            catalog_number='ADD001',
            artist='Additional Artist',
            album_name='Additional Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        # Create an exchange
        self.exchange = Exchange.objects.create(
            initiator_user=self.initiator_user,
            receiver_user=self.receiver_user,
            requested_record=self.requested_record,
            next_user_to_review=self.receiver_user
        )

        # Add initial offered records
        ExchangeOfferedRecord.objects.create(
            exchange=self.exchange,
            record=self.offered_record1
        )
        ExchangeOfferedRecord.objects.create(
            exchange=self.exchange,
            record=self.offered_record2
        )

        # Define update URL
        self.update_url = reverse('api:exchange-update', args=[self.exchange.id])

    def test_receiver_remove_all_offered_records(self):
        """
        Test receiver cannot remove all offered records
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        payload = {
            'offered_records': []  # Try to remove all records
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            ExchangeOfferedRecord.objects.filter(exchange=self.exchange).count(), 
            2  # Original count remains
        )

    def test_receiver_remove_offered_record(self):
        """
        Test receiver can remove an offered record while keeping at least one
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        payload = {
            'offered_records': [
                {'record_id': self.offered_record1.id}  # Only keep one record
            ]
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['offered_records']), 1)
        self.assertEqual(
            response.data['offered_records'][0]['record']['id'], 
            self.offered_record1.id
        )

    def test_receiver_cannot_add_offered_record(self):
        """
        Test receiver cannot add new records to offered records
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        payload = {
            'offered_records': [
                {'record_id': self.offered_record1.id},
                {'record_id': self.offered_record2.id},
                {'record_id': self.additional_record.id}  # Try to add new record
            ]
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            ExchangeOfferedRecord.objects.filter(exchange=self.exchange).count(), 
            2  # Original count remains
        )

    def test_receiver_add_requested_record(self):
        """
        Test receiver can request additional records
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        payload = {
            'offered_records': [
                {'record_id': self.offered_record1.id},
                {'record_id': self.offered_record2.id}
            ],
            'records_requested_by_receiver': [
                {'record_id': self.additional_record.id}
            ]
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['records_requested_by_receiver']), 1)
        self.assertEqual(
            response.data['records_requested_by_receiver'][0]['record']['id'],
            self.additional_record.id
        )

    def test_initiator_add_offered_record(self):
        """
        Test initiator can add new offered records
        """
        self.client.force_authenticate(user=self.initiator_user)
        self.exchange.next_user_to_review = self.initiator_user
        self.exchange.save()
        
        payload = {
            'offered_records': [
                {'record_id': self.offered_record1.id},
                {'record_id': self.offered_record2.id},
                {'record_id': self.additional_record.id}  # Add new record
            ]
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['offered_records']), 3)

    def test_initiator_remove_offered_record(self):
        """
        Test initiator can remove offered records but must keep at least one
        """
        self.client.force_authenticate(user=self.initiator_user)
        self.exchange.next_user_to_review = self.initiator_user
        self.exchange.save()
        
        # Try to remove all records
        payload = {
            'offered_records': []
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Remove one record
        payload = {
            'offered_records': [
                {'record_id': self.offered_record1.id}
            ]
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['offered_records']), 1)

    def test_initiator_handle_requested_records(self):
        """
        Test initiator handling records requested by receiver
        """
        # First have receiver request additional record
        self.client.force_authenticate(user=self.receiver_user)
        ExchangeRecordRequestedByReceiver.objects.create(
            exchange=self.exchange,
            record=self.additional_record
        )
        
        # Now test initiator's response
        self.client.force_authenticate(user=self.initiator_user)
        self.exchange.next_user_to_review = self.initiator_user
        self.exchange.save()
        
        payload = {
            'offered_records': [
                {'record_id': self.offered_record1.id},
                {'record_id': self.offered_record2.id},
                {'record_id': self.additional_record.id}  # Accept requested record
            ]
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['offered_records']), 3)
        self.assertEqual(len(response.data['records_requested_by_receiver']), 0)

    def test_wrong_user_cannot_update(self):
        """
        Test that only the next_user_to_review can update the exchange
        """
        self.client.force_authenticate(user=self.initiator_user)
        # Exchange is set for receiver to review
        
        payload = {
            'offered_records': [
                {'record_id': self.offered_record1.id}
            ]
        }
        
        response = self.client.put(self.update_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ExchangeSwitchReviewerTests(APITestCase):
    def setUp(self):
        """
        Setup test environment.
        Creates users, records, and an initial exchange for testing switch reviewer logic.
        """
        # Create test users
        self.initiator_user = User.objects.create_user(
            email='initiator@example.com',
            username='initiator',
            password='InitiatorPass123!',
            first_name='Initiator',
            last_name='User'
        )
        
        self.receiver_user = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='ReceiverPass123!',
            first_name='Receiver',
            last_name='User'
        )

        # Create required related objects
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

        # Create requested record (owned by receiver)
        self.requested_record = Record.objects.create(
            catalog_number='REC001',
            artist='Requested Artist',
            album_name='Requested Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.receiver_user
        )

        # Create record owned by initiator
        self.offered_record = Record.objects.create(
            catalog_number='OFF001',
            artist='Offered Artist',
            album_name='Offered Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        # Create additional record for receiver to request
        self.additional_record = Record.objects.create(
            catalog_number='ADD001',
            artist='Additional Artist',
            album_name='Additional Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        # Create an exchange
        self.exchange = Exchange.objects.create(
            initiator_user=self.initiator_user,
            receiver_user=self.receiver_user,
            requested_record=self.requested_record,
            next_user_to_review=self.receiver_user
        )

        # Add initial offered record
        ExchangeOfferedRecord.objects.create(
            exchange=self.exchange,
            record=self.offered_record
        )

        # Define URL
        self.switch_url = reverse('api:exchange-switch-reviewer', args=[self.exchange.id])

    def test_receiver_switch_without_requests(self):
        """
        Test receiver cannot switch reviewer if they haven't requested any additional records
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        response = self.client.post(self.switch_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.exchange.next_user_to_review, self.receiver_user)

    def test_receiver_switch_with_requests(self):
        """
        Test receiver can switch reviewer after requesting additional records
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        # Add a requested record
        ExchangeRecordRequestedByReceiver.objects.create(
            exchange=self.exchange,
            record=self.additional_record
        )
        
        response = self.client.post(self.switch_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.next_user_to_review, self.initiator_user)

    def test_initiator_switch_with_pending_requests(self):
        """
        Test initiator cannot switch reviewer while there are pending requested records
        """
        # Set initiator as next reviewer
        self.exchange.next_user_to_review = self.initiator_user
        self.exchange.save()
        
        # Add a requested record
        ExchangeRecordRequestedByReceiver.objects.create(
            exchange=self.exchange,
            record=self.additional_record
        )
        
        self.client.force_authenticate(user=self.initiator_user)
        response = self.client.post(self.switch_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.exchange.next_user_to_review, self.initiator_user)

    def test_initiator_switch_after_resolving_requests(self):
        """
        Test initiator can switch reviewer after resolving all requested records
        """
        # Set initiator as next reviewer
        self.exchange.next_user_to_review = self.initiator_user
        self.exchange.save()
        
        self.client.force_authenticate(user=self.initiator_user)
        response = self.client.post(self.switch_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.next_user_to_review, self.receiver_user)

    def test_wrong_user_cannot_switch(self):
        """
        Test that only the next_user_to_review can switch reviewer
        """
        self.client.force_authenticate(user=self.initiator_user)
        # Exchange is set for receiver to review
        
        response = self.client.post(self.switch_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.exchange.next_user_to_review, self.receiver_user)

    def test_switch_alternates_between_users(self):
        """
        Test that switch reviewer properly alternates between users
        """
        # First switch: receiver -> initiator
        self.client.force_authenticate(user=self.receiver_user)
        ExchangeRecordRequestedByReceiver.objects.create(
            exchange=self.exchange,
            record=self.additional_record
        )
        response = self.client.post(self.switch_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.next_user_to_review, self.initiator_user)
        
        # Clear requested records and add offered record
        ExchangeRecordRequestedByReceiver.objects.filter(exchange=self.exchange).delete()
        ExchangeOfferedRecord.objects.create(
            exchange=self.exchange,
            record=self.additional_record
        )
        
        # Second switch: initiator -> receiver
        self.client.force_authenticate(user=self.initiator_user)
        response = self.client.post(self.switch_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.next_user_to_review, self.receiver_user)


class ExchangeFinalizationTests(APITestCase):
    def setUp(self):
        """
        Setup test environment.
        Creates users, records, and an initial exchange for testing finalization.
        """
        # Create test users
        self.initiator_user = User.objects.create_user(
            email='initiator@example.com',
            username='initiator',
            password='InitiatorPass123!',
            first_name='Initiator',
            last_name='User'
        )
        
        self.receiver_user = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='ReceiverPass123!',
            first_name='Receiver',
            last_name='User'
        )

        # Create required related objects
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

        # Create requested record (owned by receiver)
        self.requested_record = Record.objects.create(
            catalog_number='REC001',
            artist='Requested Artist',
            album_name='Requested Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.receiver_user
        )

        # Create offered records (owned by initiator)
        self.offered_record1 = Record.objects.create(
            catalog_number='OFF001',
            artist='Offered Artist 1',
            album_name='Offered Album 1',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        self.offered_record2 = Record.objects.create(
            catalog_number='OFF002',
            artist='Offered Artist 2',
            album_name='Offered Album 2',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        # Create an exchange
        self.exchange = Exchange.objects.create(
            initiator_user=self.initiator_user,
            receiver_user=self.receiver_user,
            requested_record=self.requested_record,
            next_user_to_review=self.receiver_user
        )

        # Add offered records to exchange
        ExchangeOfferedRecord.objects.create(
            exchange=self.exchange,
            record=self.offered_record1
        )
        ExchangeOfferedRecord.objects.create(
            exchange=self.exchange,
            record=self.offered_record2
        )

        # Define URL
        self.finalize_url = reverse('api:exchange-finalize', args=[self.exchange.id])

    def test_successful_finalization(self):
        """
        Test successful finalization of exchange
        - Verifies ownership transfer
        - Verifies exchange status update
        - Verifies completion datetime is set
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        response = self.client.post(self.finalize_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh records from database
        self.requested_record.refresh_from_db()
        self.offered_record1.refresh_from_db()
        self.offered_record2.refresh_from_db()
        self.exchange.refresh_from_db()
        
        # Verify record ownership transfer
        self.assertEqual(self.requested_record.user, self.initiator_user)
        self.assertEqual(self.offered_record1.user, self.receiver_user)
        self.assertEqual(self.offered_record2.user, self.receiver_user)
        
        # Verify exchange status
        self.assertTrue(self.exchange.completed)
        self.assertIsNotNone(self.exchange.completed_datetime)

    def test_finalize_with_pending_requests(self):
        """
        Test that exchange cannot be finalized while there are pending requested records
        """
        self.client.force_authenticate(user=self.receiver_user)
        
        # Add a requested record
        ExchangeRecordRequestedByReceiver.objects.create(
            exchange=self.exchange,
            record=self.offered_record1
        )
        
        response = self.client.post(self.finalize_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.exchange.refresh_from_db()
        self.assertFalse(self.exchange.completed)

    def test_finalize_by_initiator(self):
        """
        Test that initiator cannot finalize the exchange
        """
        self.client.force_authenticate(user=self.initiator_user)
        
        response = self.client.post(self.finalize_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.exchange.refresh_from_db()
        self.assertFalse(self.exchange.completed)

    def test_finalize_already_completed(self):
        """
        Test that a completed exchange cannot be finalized again
        """
        # First, complete the exchange
        self.client.force_authenticate(user=self.receiver_user)
        self.client.post(self.finalize_url)
        
        # Try to complete it again
        response = self.client.post(self.finalize_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finalize_cleans_up_related_exchanges(self):
        """
        Test that finalization removes other exchanges involving the same records
        """
        # Create another user who wants the same records
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='OtherPass123!',
            first_name='Other',
            last_name='User'
        )

        # Create a record that other_user will offer
        other_record = Record.objects.create(
            catalog_number='OTHER001',
            artist='Other Artist',
            album_name='Other Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=other_user
        )

        # Create another exchange where other_user requests one of the offered records
        other_exchange = Exchange.objects.create(
            initiator_user=other_user,
            receiver_user=self.initiator_user,
            requested_record=self.offered_record1,  # This record is part of our main exchange
            next_user_to_review=self.initiator_user,
            completed=False
        )
        
        # Add offered record to the other exchange
        ExchangeOfferedRecord.objects.create(
            exchange=other_exchange,
            record=other_record
        )
        
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.post(self.finalize_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify other exchange was deleted
        with self.assertRaises(Exchange.DoesNotExist):
            other_exchange.refresh_from_db()

    def test_finalize_unauthenticated(self):
        """
        Test that unauthenticated user cannot finalize exchange
        """
        response = self.client.post(self.finalize_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.exchange.refresh_from_db()
        self.assertFalse(self.exchange.completed)


class ExchangeDeleteTests(APITestCase):
    def setUp(self):
        """
        Setup test environment.
        Creates users, records, and exchanges for testing deletion.
        """
        # Create test users
        self.initiator_user = User.objects.create_user(
            email='initiator@example.com',
            username='initiator',
            password='InitiatorPass123!',
            first_name='Initiator',
            last_name='User'
        )
        
        self.receiver_user = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='ReceiverPass123!',
            first_name='Receiver',
            last_name='User'
        )

        # Create required related objects
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

        # Create requested record (owned by receiver)
        self.requested_record = Record.objects.create(
            catalog_number='REC001',
            artist='Requested Artist',
            album_name='Requested Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.receiver_user
        )

        # Create offered record (owned by initiator)
        self.offered_record = Record.objects.create(
            catalog_number='OFF001',
            artist='Offered Artist',
            album_name='Offered Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user
        )

        # Create active exchange
        self.active_exchange = Exchange.objects.create(
            initiator_user=self.initiator_user,
            receiver_user=self.receiver_user,
            requested_record=self.requested_record,
            next_user_to_review=self.receiver_user
        )

        # Add offered record to active exchange
        ExchangeOfferedRecord.objects.create(
            exchange=self.active_exchange,
            record=self.offered_record
        )

        # Create completed exchange
        self.completed_exchange = Exchange.objects.create(
            initiator_user=self.initiator_user,
            receiver_user=self.receiver_user,
            requested_record=self.requested_record,
            next_user_to_review=self.receiver_user,
            completed=True
        )

        # Define URLs
        self.delete_active_url = reverse('api:exchange-delete', args=[self.active_exchange.id])
        self.delete_completed_url = reverse('api:exchange-delete', args=[self.completed_exchange.id])

    def test_initiator_can_delete_active_exchange(self):
        """
        Test that initiator can delete/cancel an active exchange
        """
        self.client.force_authenticate(user=self.initiator_user)
        response = self.client.delete(self.delete_active_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify exchange was deleted
        with self.assertRaises(Exchange.DoesNotExist):
            self.active_exchange.refresh_from_db()
            
        # Verify records still exist with original owners
        self.requested_record.refresh_from_db()
        self.offered_record.refresh_from_db()
        self.assertEqual(self.requested_record.user, self.receiver_user)
        self.assertEqual(self.offered_record.user, self.initiator_user)

    def test_receiver_can_delete_active_exchange(self):
        """
        Test that receiver can delete/cancel an active exchange
        """
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.delete(self.delete_active_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify exchange was deleted
        with self.assertRaises(Exchange.DoesNotExist):
            self.active_exchange.refresh_from_db()

    def test_cannot_delete_completed_exchange(self):
        """
        Test that a completed exchange cannot be deleted
        """
        self.client.force_authenticate(user=self.initiator_user)
        response = self.client.delete(self.delete_completed_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify exchange still exists
        self.completed_exchange.refresh_from_db()
        self.assertTrue(self.completed_exchange.completed)

    def test_non_participant_cannot_delete_exchange(self):
        """
        Test that a user who is not part of the exchange cannot delete it
        """
        other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='OtherPass123!',
            first_name='Other',
            last_name='User'
        )
        
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(self.delete_active_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify exchange still exists
        self.active_exchange.refresh_from_db()

    def test_delete_exchange_with_requested_records(self):
        """
        Test deleting exchange that has records requested by receiver
        """
        # Add a requested record
        ExchangeRecordRequestedByReceiver.objects.create(
            exchange=self.active_exchange,
            record=self.offered_record
        )
        
        self.client.force_authenticate(user=self.initiator_user)
        response = self.client.delete(self.delete_active_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify all related records are deleted
        self.assertEqual(
            ExchangeRecordRequestedByReceiver.objects.filter(
                exchange=self.active_exchange
            ).count(),
            0
        )

    def test_delete_unauthenticated(self):
        """
        Test that unauthenticated user cannot delete exchange
        """
        response = self.client.delete(self.delete_active_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify exchange still exists
        self.active_exchange.refresh_from_db()


class SeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Firefox()
        populate_db()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login(self):
        self.driver.get(f'http://localhost:5173/')  # Otvaranje React aplikacije
        
        auth_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'auth-button'))
        )
        auth_button.click()

        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login-button'))
        )
        login_button.click()

        email_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        password_field = self.driver.find_element(By.NAME, 'password')
        login_submit = self.driver.find_element(By.CSS_SELECTOR, '[type="submit"]')

        email_field.send_keys('testuser@example.com')
        password_field.send_keys('TestPass123!')
        login_submit.click()

        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
        self.assertIsNotNone(success_message)
