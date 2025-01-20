from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import *


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
