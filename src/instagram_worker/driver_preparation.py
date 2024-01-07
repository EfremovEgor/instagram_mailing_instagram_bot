import config

from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from .instagram_dataclasses import DriverSettings


def get_default_options(driver_settings: DriverSettings) -> Options:
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    if driver_settings.proxy_url is not None:
        options.add_argument(f"--proxy-server={config.PROXY_SERVER_URL}")
    return options


def get_driver(driver_settings: DriverSettings) -> webdriver.Chrome:
    options = get_default_options(driver_settings)
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    return driver
