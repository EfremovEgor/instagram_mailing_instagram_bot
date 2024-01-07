import random
import time
import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)

from .element_paths import XPaths, CSSClasses
from .instagram_dataclasses import (
    AccountDetails,
    BotSettings,
    DriverSettings,
    Message,
    MessageThread,
)
from .driver_preparation import get_driver
from .exceptions import SearchNotAvailableException

from bs4 import BeautifulSoup
from utilities import sleep


class Instagram:
    def __init__(
        self,
        account_details: AccountDetails,
        settings: BotSettings,
        driver_settings: DriverSettings,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        try:
            self.account_details = account_details
            self.driver = get_driver(driver_settings)
            self.delay_range = settings.interaction_interval
            self.name = settings.name
            self.cookies_path = settings.cookies_path
        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)

    def wait_for_redirect(self) -> None:
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_changes(self.driver.current_url)
            )
        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)

    @sleep
    def open_url(
        self, url: str = "https://www.instagram.com/"
    ) -> tuple[bool, None | Exception]:
        try:
            self.driver.get(url)
            self.logger.info(f"Opened url: {url}")
            return True, None
        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)
            return False, ex

    @sleep
    def accept_cookies(self) -> tuple[bool, None | Exception]:
        self.logger.info(f"Trying to accept cookies")

        try:
            self.driver.find_element(
                By.XPATH, XPaths.get_xpath("accept_cookies_button")
            ).click()
            self.logger.info("Accept cookies button pressed")

            return True, None
        except NoSuchElementException:
            self.logger.exception("No accept cookies button present", stack_info=True)
            return True, None
        except Exception as ex:
            return False, ex

    @sleep
    def login(self) -> tuple[bool, None | Exception]:
        self.logger.info(f"Trying to login")

        try:
            self.driver.find_element(
                By.XPATH, XPaths.get_xpath("login_field")
            ).send_keys(self.account_details.login)
            self.logger.info("Login entered")

            time.sleep(random.randint(*self.delay_range))

            self.driver.find_element(
                By.XPATH, XPaths.get_xpath("password_field")
            ).send_keys(self.account_details.password)
            self.logger.info("Password entered")

            time.sleep(random.randint(*self.delay_range))

            self.driver.find_element(By.XPATH, XPaths.get_xpath("login_button")).click()
            self.logger.info("Login button pressed")

            return True, None
        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)

            return False, ex

    @sleep
    def disable_notifications(self) -> tuple[bool, None | Exception]:
        self.logger.info(f"Trying to disable notifications")

        try:
            self.driver.find_element(
                By.XPATH, XPaths.get_xpath("disable_notifications_button")
            ).click()

            self.logger.info("Disable notifications button pressed")

            return True, None
        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)

            return False, ex

    @sleep
    def open_direct(self) -> tuple[bool, None | Exception]:
        self.logger.info(f"Trying to open direct")

        try:
            try:
                self.driver.find_element(
                    By.XPATH, XPaths.get_xpath("direct_button")
                ).click()
                self.logger.info("Direct button clicked")

            except NoSuchElementException as ex:
                self.logger.exception(str(ex), stack_info=True)

                self.driver.get("https://www.instagram.com/direct/inbox/")
            return True, None
        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)

            return False, ex

    def __parse_html_for_new_messages(self, html: str) -> dict:
        self.logger.info(f"Trying to parse html for new messages")

        html_objects = BeautifulSoup(html, "lxml")
        unread_markers = html_objects.find_all(
            "span", {"data-visualcompletion": "ignore"}
        )
        messages = dict()
        for marker in unread_markers:
            username = (
                list(marker.parent.parent.parent.parent.children)[1]
                .select(
                    "span."
                    + ".".join(
                        CSSClasses.get_css_class(
                            "direct_message_container_username"
                        ).split()
                    )
                )[0]
                .text
            )
            message = (
                list(marker.parent.parent.parent.parent.children)[1]
                .select(
                    "span."
                    + ".".join(
                        CSSClasses.get_css_class(
                            "direct_message_container_username"
                        ).split()
                    )
                )[1]
                .text
            )
            messages[username] = message
        return messages

    @sleep
    def get_new_messages(
        self,
    ) -> tuple[bool, list[MessageThread] | Exception]:
        self.logger.info(f"Trying to get new messages")

        try:
            random.choice([self.driver.refresh, self.open_direct])()
            threads = list()
            indicators = self.driver.find_elements(
                By.CSS_SELECTOR,
                f"span[class='{CSSClasses.get_css_class('direct_new_message_indicator')}']",
            )
            self.logger.info(f"{len(indicators)} new message indicators found")

            for indicator in indicators:
                indicator.find_element(By.XPATH, "..").find_element(
                    By.XPATH, ".."
                ).find_element(By.XPATH, "..").find_element(
                    By.XPATH, ".."
                ).find_element(
                    By.XPATH, ".."
                ).find_element(
                    By.XPATH, ".."
                ).click()
                self.logger.info("Opened dialog")

                time.sleep(random.randint(*self.delay_range))

                username = self.driver.find_element(
                    By.XPATH, XPaths.get_xpath("message_container_username")
                ).text
                self.logger.info(f"Got username {username}")

                thread = MessageThread(username)
                messages = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    f"div[class*='x6prxxf x1fc57z9 x1yc453h x126k92a']",
                )
                self.logger.info(f"{len(messages)} found messages")

                for message in messages:
                    if "x14ctfv" in message.get_attribute("class"):
                        sender = "you"
                    if "xzsf02u" in message.get_attribute("class"):
                        sender = username
                    thread.messages.append(Message(sender, message.text))
                threads.append(thread)

        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)

            return False, ex
        return True, threads

    def __open_chat_through_direct(self, username: str) -> None:
        self.logger.info(f"Trying to open chat through direct")

        self.open_direct()
        self.driver.find_element(
            By.XPATH, XPaths.get_xpath("direct_send_message_button")
        ).click()
        self.logger.info("Clicked send message in direct")

        time.sleep(random.randint(*self.delay_range))

        self.driver.find_element(By.NAME, "queryBox").send_keys(username)
        self.logger.info(f"Username '{username}' entered")

        time.sleep(random.randint(*self.delay_range))

        username = self.driver.find_elements(By.XPATH, f"//*[text()='{username}']")[-1]
        self.logger.info(f"Found username '{username}'")

        username.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(
            By.XPATH, ".."
        ).find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(
            By.XPATH, ".."
        ).find_element(
            By.XPATH, ".."
        ).find_element(
            By.XPATH, ".."
        ).click()
        self.logger.info(f"Clicked username '{username}' to select it")

        time.sleep(random.randint(*self.delay_range))

        self.driver.find_element(
            By.XPATH, XPaths.get_xpath("direct_search_chat_button")
        ).click()
        self.logger.info("Chat button clicked")

        time.sleep(random.randint(*self.delay_range))

    def __open_chat_through_global_search(self, username: str) -> None:
        self.logger.info(f"Trying to open chat through global search")

        self.driver.find_element(
            By.XPATH, XPaths.get_xpath("global_search_button")
        ).click()
        self.logger.info("Clicked global search button")

        time.sleep(random.randint(*self.delay_range))

        self.driver.find_element(
            By.XPATH, XPaths.get_xpath("global_search_input")
        ).send_keys(username)
        self.logger.info(f"Entered username '{username}' to search box")

        time.sleep(random.randint(*self.delay_range))

        usernames = self.driver.find_elements(By.XPATH, f"//span[text()='{username}']")
        if len(usernames) == 1 or len(usernames) == 2:
            username = usernames[-1]
        else:
            username = usernames[1]
        self.logger.info(f"Found username '{username}' in search box")

        try:
            username.find_element(By.XPATH, "..").find_element(
                By.XPATH, ".."
            ).find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).click()
            self.logger.info(f"Clicked '{username}' to open profile")

        except ElementClickInterceptedException:
            username.find_element(By.XPATH, "..").find_element(
                By.XPATH, ".."
            ).find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).find_element(
                By.XPATH, ".."
            ).click()

            self.logger.info(
                f"Clicked username '{username}' to open profile trying to use second method"
            )

        time.sleep(random.randint(*self.delay_range))
        try:
            button = self.driver.find_element(
                By.XPATH, XPaths.get_xpath("profile_send_message_button")
            )

            if button.text.strip() != "Отправить сообщение":
                raise Exception()
            button.click()

            self.logger.info("Clicked send message button to enter chat")
            time.sleep(random.randint(*self.delay_range))

        except NoSuchElementException:
            self.logger.info(
                "No send message button found, trying to use second method"
            )

            self.driver.find_element(
                By.XPATH, XPaths.get_xpath("profile_subscribe_button")
            ).click()
            self.logger.info("Subscribed to a person")

            time.sleep(random.randint(*self.delay_range))
        try:
            self.driver.find_element(
                By.XPATH, XPaths.get_xpath("type_message_container")
            )
            self.logger.info("Opened chat")

        except NoSuchElementException:
            self.logger.info("Cannot open chat trying to use second method")

            self.driver.find_element(
                By.XPATH, XPaths.get_xpath("profile_send_message_button")
            ).click()
            self.logger.info("Opened chat using second method")

        time.sleep(random.randint(*self.delay_range))

    def __chat_send_message(self, message: str) -> None:
        try:
            type_message_container = self.driver.find_element(
                By.XPATH, XPaths.get_xpath("type_message_container")
            )

            message_container = type_message_container.find_element(By.TAG_NAME, "p")
            self.logger.info("Message chatbox found")

            for line in message.split("\n"):
                message_container.send_keys(line)
                message_container.send_keys(Keys.SHIFT, Keys.ENTER)
                time.sleep(random.randint(1, 3))
            self.logger.info("Message entered")

            time.sleep(random.randint(*self.delay_range))
            # self.driver.find_element(
            #     By.XPATH, XPaths.get_xpath("type_message_send_button")
            # ).click(),
            random.choice(
                [
                    type_message_container.send_keys(Keys.ENTER),
                ]
            )

            self.logger.info("Message sent")

        except NoSuchElementException as ex:
            self.logger.exception(str(ex), stack_info=True)

            raise SearchNotAvailableException()

    @sleep
    def send_message(
        self, message: str, username: str
    ) -> tuple[bool, None | Exception]:
        self.logger.info(f"Trying to send message to {username}")

        choices = [
            self.__open_chat_through_global_search,
            self.__open_chat_through_direct,
        ]

        try:
            choice = random.choices([0, 1], [30, 70])[0]
            choices.pop(choice)(username)
            self.__chat_send_message(message)

        except Exception as ex:
            self.logger.exception(str(ex), stack_info=True)
            self.open_direct()
            return False, ex
        self.open_direct()
        return True, None

    def challenges_handler(self) -> None:
        ...
