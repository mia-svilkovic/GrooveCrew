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

    def test_successful_wishlist_entry_removal(self):
        self.perform_login('testuser@example.com', 'TestPass123!')

        menu_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'menu_button'))
        )
        menu_button.click()

        wishlist_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'button_Wishlist'))
        )
        wishlist_button.click()

        delete_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'wishlist-remove'))
        )
        delete_button.click()

        # Verify success message
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
        self.assertIsNotNone(success_message)
        self.assertTrue(success_message.is_displayed())
