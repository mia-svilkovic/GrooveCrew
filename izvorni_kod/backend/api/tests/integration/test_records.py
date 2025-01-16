from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.contrib.gis.geos import Point
from api.models import *
from .base import BaseSeleniumTestCase


class RecordsTests(BaseSeleniumTestCase):
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

        self.frontend_url = "http://localhost:5173"

    def test_unsuccessful_record_add(self):
        self.perform_login('testuser@example.com', 'TestPass123!')

        add_record_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'open-add-button'))
        )
        add_record_button.click()

        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.form-container>form'))
        )

        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )
        submit_button.click()

        is_valid = self.driver.execute_script("return arguments[0].checkValidity();", form)

        self.assertFalse(is_valid)


    def test_successful_record_update(self):
        self.perform_login('testuser@example.com', 'TestPass123!')

        menu_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'menu_button'))
        )
        menu_button.click()

        my_vinyls_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'button_Myvinyls'))
        )
        my_vinyls_button.click()

        open_edit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.open-edit-button'))
        )
        open_edit_button.click()

        catalog_number_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'catalogNumber'))
        )
        artist_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'artist'))
        )
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )

        catalog_number_field.send_keys("QQQQQ-00000")
        artist_field.send_keys("The Best Artist")
        submit_button.click()

        # Verify success message
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
        self.assertIsNotNone(success_message)
        self.assertTrue(success_message.is_displayed())
