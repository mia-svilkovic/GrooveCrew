from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from api.models import User
from .base import BaseSeleniumTestCase


class AuthenticationTests(BaseSeleniumTestCase):
    def setUp(self):
        """Create test user before each test"""
        super().setUp()
        self.test_user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )

    def test_successful_login(self):
        """
        Test successful login flow:
        1. Navigate to home page
        2. Click auth button
        3. Click login button
        4. Fill in credentials
        5. Submit form
        6. Verify success message
        """
        # Navigate to home page
        self.driver.get(self.frontend_url)

        # Click auth button
        auth_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'auth-button'))
        )
        auth_button.click()

        # Click login button
        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login-button'))
        )
        login_button.click()

        # Fill in login form
        email_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        login_submit = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )

        email_field.send_keys('testuser@example.com')
        password_field.send_keys('TestPass123!')
        login_submit.click()

        # Verify success message
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
        self.assertIsNotNone(success_message)
        self.assertTrue(success_message.is_displayed())

    def test_login_with_invalid_credentials(self):
        """
        Test login with invalid credentials:
        1. Navigate to login form
        2. Fill in wrong credentials
        3. Verify error message
        """
       
        # Navigate to home page
        self.driver.get(self.frontend_url)

        # Click auth button
        auth_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'auth-button'))
        )
        auth_button.click()

        # Click login button
        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login-button'))
        )
        login_button.click()

        # Fill in login form
        email_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        login_submit = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )

        email_field.send_keys('wrong@example.com')
        password_field.send_keys('WrongPass123!')
        login_submit.click()

        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        self.assertIsNotNone(error_message)
        self.assertTrue(error_message.is_displayed())
        self.assertIn('Invalid credentials', error_message.text)
