from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.contrib.gis.geos import Point
from api.models import *
from .base import BaseSeleniumTestCase


class ExchangeTests(BaseSeleniumTestCase):
    def setUp(self):
        """
        Setup test cases with necessary users and records.
        Creates two users:
        - initiator_user: who will initiate the exchange
        - receiver_user: who owns the requested record
        """
        super().setUp()

        # Create test users
        self.initiator_user = User.objects.create_user(
            email='initiator@example.com',
            username='initiator',
            password='TestPass123!',
            first_name='Initiator',
            last_name='User'
        )
        
        self.receiver_user = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='TestPass123!',
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

        self.additionally_requested_record = Record.objects.create(
            catalog_number='REQ001',
            artist='Additionally requested Artist',
            album_name='Additionally requested Album',
            release_year=2020,
            genre=self.genre,
            location=self.location,
            record_condition=self.record_condition,
            cover_condition=self.cover_condition,
            user=self.initiator_user,
            additional_description='Record to be additionally requested by offer receiver'
        )

    def test_successful_exchange(self):
        self.perform_login(self.initiator_user.email, 'TestPass123!')

        exchange_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.vinyl-item button'))
        )
        exchange_button.click()

        offer_vinyl_checkboxes = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'label.check-option input[type="checkbox"]'))
        )
        for i in range(2):
            offer_vinyl_checkboxes[i].click()

        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )
        submit_button.click()

        self.perform_login(self.receiver_user.email, 'TestPass123!')

        menu_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'menu_button'))
        )
        menu_button.click()

        offers_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'button_Offers'))
        )
        offers_button.click()

        request_additional_record_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.exchange-actions > button'))
        )
        request_additional_record_button.click()

        request_vinyl_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'label.check-option input[type="checkbox"]'))
        )
        request_vinyl_checkbox.click()

        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )
        submit_button.click()

        finalize_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'review-button'))
        )
        finalize_button.click()

        self.perform_login(self.initiator_user.email, 'TestPass123!')

        menu_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'menu_button'))
        )
        menu_button.click()

        offers_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'button_Offers'))
        )
        offers_button.click()

        accept_additionally_requested_record_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.record-decision-buttons > button'))
        )
        accept_additionally_requested_record_button.click()

        finalize_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'review-button'))
        )
        finalize_button.click()

        self.perform_login(self.receiver_user.email, 'TestPass123!')

        menu_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'menu_button'))
        )
        menu_button.click()

        offers_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'button_Offers'))
        )
        offers_button.click()

        finalize_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'finalize-button'))
        )
        finalize_button.click()

        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
        self.assertIsNotNone(success_message)
        self.assertTrue(success_message.is_displayed())


    def test_unsuccessful_exchange(self):
        self.perform_login(self.initiator_user.email, 'TestPass123!')

        exchange_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.vinyl-item button'))
        )
        exchange_button.click()

        offer_vinyl_checkboxes = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'label.check-option input[type="checkbox"]'))
        )
        for i in range(2):
            offer_vinyl_checkboxes[i].click()

        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )
        submit_button.click()

        self.perform_login(self.receiver_user.email, 'TestPass123!')

        menu_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'menu_button'))
        )
        menu_button.click()

        offers_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'button_Offers'))
        )
        offers_button.click()

        offer_vinyl_checkboxes = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'remove-button'))
        )
        for checkbox in offer_vinyl_checkboxes:
            checkbox.click()

        finalize_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'finalize-button'))
        )
        finalize_button.click()

        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        self.assertIsNotNone(error_message)
        self.assertTrue(error_message.is_displayed())
