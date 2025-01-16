from selenium.webdriver.common.by import By
from .base import BaseSeleniumTestCase
from api.models import User

class AuthenticationSeleniumTests(BaseSeleniumTestCase):
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
        self.frontend_url = "http://localhost:5173"

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
        auth_button = self.wait_for_element(By.ID, 'auth-button')
        auth_button.click()

        # Click login button
        login_button = self.wait_for_element(By.ID, 'login-button')
        login_button.click()

        # Fill in login form
        email_field = self.wait_for_element(By.NAME, 'email')
        password_field = self.wait_for_element(By.NAME, 'password')
        login_submit = self.wait_for_element(By.CSS_SELECTOR, '[type="submit"]')

        email_field.send_keys('testuser@example.com')
        password_field.send_keys('TestPass123!')
        login_submit.click()

        # Verify success message
        success_message = self.wait_for_element(By.CLASS_NAME, 'success-message')
        self.assertIsNotNone(success_message)
        self.assertTrue(success_message.is_displayed())

    def test_login_with_invalid_credentials(self):
        """
        Test login with invalid credentials:
        1. Navigate to login form
        2. Fill in wrong credentials
        3. Verify error message
        """
        self.driver.get(self.frontend_url)
        
        auth_button = self.wait_for_element(By.ID, 'auth-button')
        auth_button.click()
        
        login_button = self.wait_for_element(By.ID, 'login-button')
        login_button.click()

        email_field = self.wait_for_element(By.NAME, 'email')
        password_field = self.wait_for_element(By.NAME, 'password')
        login_submit = self.wait_for_element(By.CSS_SELECTOR, '[type="submit"]')

        email_field.send_keys('wrong@example.com')
        password_field.send_keys('WrongPass123!')
        login_submit.click()

        error_message = self.wait_for_element(By.CLASS_NAME, 'error-message')
        self.assertIsNotNone(error_message)
        self.assertTrue(error_message.is_displayed())
        self.assertIn('Invalid credentials', error_message.text)