from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point
from ...models import *


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
