from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import subprocess, time, os, signal, psutil


class BaseSeleniumTestCase(StaticLiveServerTestCase):
    """
    Base class for Selenium tests providing common functionality
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(10)
        cls.frontend_url = "http://localhost:5173"
        
        # Get the current file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the 'frontend' directory
        frontend_dir = os.path.abspath(os.path.join(current_dir, '../../../../frontend'))

        # Start Vite with modified API URL
        os.environ['VITE_API_URL'] = cls.live_server_url
        print(f"Setting VITE_API_URL to: {cls.live_server_url}")
        cls.vite_process = subprocess.Popen(
            ['npm', 'run', 'dev'], 
            cwd=frontend_dir,
            env=os.environ,
            stdin=subprocess.PIPE,  # Redirect stdin to avoid terminal interaction
            stdout=subprocess.DEVNULL,  # Optional: Suppress stdout
            stderr=subprocess.DEVNULL,  # Optional: Suppress stderr
        )
        # Wait for Vite to start
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        # Kill Vite process and all its children
        if hasattr(cls, 'vite_process') and cls.vite_process:
            vite_pid = cls.vite_process.pid
            cls._kill_process_tree(vite_pid)
            cls.vite_process = None

        if 'VITE_API_URL' in os.environ:
            del os.environ['VITE_API_URL']
            
        cls.driver.quit()
        super().tearDownClass()

    @staticmethod
    def _kill_process_tree(pid, sig=signal.SIGTERM):
        """
        Kill a process tree (including children) given a parent PID.
        """
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.send_signal(sig)
            parent.send_signal(sig)
        except psutil.NoSuchProcess:
            pass

    def clean_session(self):
        """Clean up browser session"""
        # First navigate to the page
        self.driver.get('http://localhost:5173')
        # Then clear storage and cookies
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.delete_all_cookies()
        self.driver.refresh()
        time.sleep(1)  # Give time for the refresh to complete
        
    def perform_login(self, email, password):
        """Helper method to perform login with fresh session"""
        self.clean_session()
        self.driver.get('http://localhost:5173')
        
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

        email_field.send_keys(email)
        password_field.send_keys(password)
        login_submit.click()

        # Wait for modal to disappear
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "modal-overlay"))
        )
