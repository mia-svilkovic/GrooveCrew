from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ...management.commands.populate_db import populate_db
from ...models import *


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
        self.driver.get(f'http://localhost:5173/')
        
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
