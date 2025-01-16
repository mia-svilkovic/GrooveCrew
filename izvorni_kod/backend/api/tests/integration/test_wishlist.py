from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from api.models import User, Wishlist
from .base import BaseSeleniumTestCase


class WishlistTests(BaseSeleniumTestCase):
    def setUp(self):
        """Create test user before each test"""
        super().setUp()

        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        self.wishlist_item = Wishlist.objects.create(
            user=self.user,
            record_catalog_number='TEST001'
        )

        self.frontend_url = "http://localhost:5173"

    def test_successful_wishlist_entry_removal(self):
        self.driver.get(self.frontend_url)

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
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        login_submit = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )

        email_field.send_keys('testuser@example.com')
        password_field.send_keys('TestPass123!')
        login_submit.click()

        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "modal-overlay"))
        )

        menu_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'menu_button'))
        )
        menu_button.click()

        wishlist_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'button_Wishlist'))
        )
        wishlist_button.click()

        delete_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.wishlist-list>.wishlist-item>.wishlist-remove'))
        )
        delete_button.click()

        # Verify success message
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
        self.assertIsNotNone(success_message)
        self.assertTrue(success_message.is_displayed())
