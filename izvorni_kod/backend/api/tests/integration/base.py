from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time
import os
import psutil
import signal

class BaseSeleniumTestCase(StaticLiveServerTestCase):
    """
    Base class for Selenium tests providing common functionality
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(10)
        
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

    def wait_for_element(self, by, value, timeout=10):
        """Helper method to wait for and return an element"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by, value, timeout=10):
        """Helper method to wait for and return a clickable element"""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
