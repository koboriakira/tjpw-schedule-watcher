"""Selenium factory and utilities."""

import os

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


class NotReadyError(Exception):
    """Selenium is not ready."""

    pass


class SeleniumFactory:
    """Factory for creating Selenium WebDriver."""

    @staticmethod
    def create() -> webdriver.Remote:
        """Create Selenium WebDriver.

        Returns:
            WebDriver instance

        Raises:
            NotReadyError: If Selenium is not ready
        """
        selenium_domain = os.environ.get("SELENIUM_DOMAIN", "http://localhost:4444")

        try:
            options = webdriver.ChromeOptions()
            driver = webdriver.Remote(
                command_executor=selenium_domain,
                options=options,
            )
            driver.implicitly_wait(5)  # 5 seconds timeout
            return driver
        except WebDriverException as e:
            raise NotReadyError(f"Selenium is not ready at {selenium_domain}: {e}") from e

    @staticmethod
    def validate() -> None:
        """Validate Selenium connection.

        Raises:
            NotReadyError: If Selenium is not ready
        """
        try:
            driver = SeleniumFactory.create()
            driver.quit()
        except Exception as e:
            raise NotReadyError(f"Selenium validation failed: {e}") from e
