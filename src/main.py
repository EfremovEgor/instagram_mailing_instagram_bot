import datetime
import pytz
import logging
import config
import time
import random
import os

from string import Template
from instagram_worker import Instagram
from instagram_worker.instagram_dataclasses import (
    AccountDetails,
    BotSettings,
    DriverSettings,
    Message,
    MessageThread,
)
from dataclasses import dataclass
from database import Session
from database import models

logger = logging.getLogger(__name__)


@dataclass
class MailingTarget:
    status: str
    sex: str
    username: str
    worker: str | None
    first_name: str


def get_greeting() -> str:
    greetings = {
        "default": ["Здравствуйте", "Привет"],
        "morning": ["Добррое утро"],
        "afternoon": ["Добрый день"],
        "evening": ["Добрый вечер"],
    }
    time = datetime.datetime.now(pytz.timezone("Europe/Moscow"))

    def get_time_of_day(time: int) -> str:
        if time < 12:
            return "morning"
        elif time < 16:
            return "afternoon"
        else:
            return "evening"

    choices = greetings["default"]
    choices.extend(greetings[get_time_of_day(time.hour)])
    return random.choice(choices)


def create_message(data: dict = None) -> str:
    if data is None:
        data = dict()
    random.choice(config.MESSAGE_TEMPLATES)
    message = Template(random.choice(config.MESSAGE_TEMPLATES))
    message = message.safe_substitute(greeting=get_greeting(), **data).strip()
    if data.get("first_name") == None:
        message = message.replace(", $first_name", "")
    return message


def get_target_for_mailing(session: Session) -> models.MailingTarget | None:
    target = (
        session.query(models.MailingTarget)
        .filter(models.MailingTarget.status == "PENDING")
        .first()
    )

    return target


def notify_about_new_messages(
    instagram_instance: Instagram,
    session: Session,
) -> None:
    logger.info("Starting notifying about new messages")

    status, data = instagram_instance.get_new_messages()

    if (not status) and data is not None:
        logger.info("No unread threads")
        return
    unread_messages_threads: list[MessageThread] = data
    if not unread_messages_threads:
        logger.info("No unread messages")

        return
    message_threads_instances = list()
    new_messages_notifiers_instances = list()

    for message_thread in unread_messages_threads:
        logger.info(f"Starting to work with thread with {message_thread.username}")

        session.query(models.MessageThread).filter(
            models.MessageThread.worker == instagram_instance.name,
            models.MessageThread.thread_username == message_thread.username,
        ).delete()
        logger.info(f"Deleted all messages from {message_thread.username}")

        mailing_target = (
            session.query(models.MailingTarget)
            .filter(
                models.MailingTarget.username == message_thread.username,
                models.MailingTarget.worker == instagram_instance.name,
            )
            .first()
        )
        if mailing_target is not None:
            mailing_target.was_answered_by_target = True
            session.commit()
            logger.info(
                f"Set was_answered_by_target of {mailing_target.username} to True"
            )

        new_message = message_thread.messages[-1]
        new_message_query = (
            session.query(models.NewMessage)
            .filter(
                models.NewMessage.worker == instagram_instance.name,
                models.NewMessage.sender_username == new_message.sender,
            )
            .first()
        )
        if new_message_query is None:
            new_messages_notifiers_instances.append(
                models.NewMessage(
                    worker=instagram_instance.name,
                    message=new_message.message,
                    sender_username=new_message.sender,
                )
            )

        for message in message_thread.messages:
            message_threads_instances.append(
                models.MessageThread(
                    worker=instagram_instance.name,
                    message=message.message,
                    sender_username=message.sender,
                    thread_username=message_thread.username,
                )
            )
    session.add_all(message_threads_instances)
    session.add_all(new_messages_notifiers_instances)

    session.commit()
    logger.info(f"Added all new messages and message threads to database")
    status, exception = instagram_instance.open_direct()
    if status:
        logger.info("Reopened direct")
        return

    logger.exception("Couldn't reopen direct")
    logger.exception(str(exception), stack_info=True)


def reply_new_messages(
    instagram_instance: Instagram,
    session: Session,
) -> None:
    logger.info("Starting to reply vacant person")

    message: models.NewMessage = (
        session.query(models.NewMessage)
        .filter(
            models.NewMessage.answer is not None
            and models.NewMessage.status == "ANSWERED"
            and models.NewMessage.worker == instagram_instance.name,
        )
        .first()
    )
    if message is None:
        logger.info("No new messages from admin found")
        return

    status, exception = instagram_instance.send_message(
        message=message.answer, username=message.sender_username
    )

    if not status:
        logger.exception(
            f"Couldn't reply to message from {message.sender_username}", stack_info=True
        )
        logger.exception(str(exception))
        return

    session.delete(message)
    session.commit()
    logger.info("Deleted replied message from database")

    print(
        f"Answered message '{message.answer}' in thread with {message.sender_username}"
    )
    logger.info(f"Answered message in thread with {message.sender_username}")

    status, exception = instagram_instance.open_direct()
    if status:
        logger.info("Reopened direct")
        return

    logger.exception("Couldn't reopen direct")
    logger.exception(str(exception), stack_info=True)


def mail_vacant_person(
    instagram_instance: Instagram,
    session: Session,
) -> None:
    logger.info("Starting to mail vacant person")

    target: models.MailingTarget = get_target_for_mailing(session)

    logger.info(f"Random target selected: {target.username}")

    if target is None:
        logger.info("No pending targets to mail")
        return

    target.status = "WORKING"
    target.worker = instagram_instance.name
    session.commit()
    logger.info("Set target status to WORKING")

    message = create_message(
        {
            "sex": target.sex,
            "first_name": target.first_name,
        }
    )
    logger.info("Random message created")

    status, exception = instagram_instance.send_message(message, target.username)
    if exception is not None:
        logger.exception(f"Couldn't mail {target.username}")

        target.status = "PENDING"
        target.worker = None
        session.commit()
        logger.exception(f"Changed target's status to PENDING")
        return

    logger.info(f"Finished sending message to {target.username}")

    target.status = "DONE"
    target.was_answered_by_target = False
    target.done_at = datetime.datetime.now(pytz.utc)
    session.commit()
    logger.info(f"Set target's status to DONE at {target.done_at}")

    status, exception = instagram_instance.open_direct()
    if status:
        logger.info("Reopened direct")
        return

    logger.exception("Couldn't reopen direct")
    logger.exception(str(exception), stack_info=True)


def init_logger() -> None:
    logs_folder = os.path.join(os.getcwd(), "logs")
    if not logs_folder:
        os.mkdir(logs_folder)

    filename = os.path.join(
        logs_folder, datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + ".log"
    )
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s: %(levelname)s] %(message)s",
        filename=filename,
        filemode="w",
    )


def main() -> None:
    init_logger()

    logger.setLevel(level=logging.INFO)

    logger_selenium = logging.getLogger("selenium")
    logger_selenium.setLevel(logging.INFO)

    logger.info("Logger setupped")
    time_next_new_messages_check = 0
    time_send_next_message = 0
    time_next_answers_check = 0

    session = Session()
    logger.info("Database session created")

    instagram_instance = Instagram(
        AccountDetails(
            login=config.INSTAGRAM_LOGIN,
            password=config.INSTAGRAM_PASSWORD,
        ),
        BotSettings(
            name=config.BOT_NAME,
            interaction_interval=config.PAGE_INTERACTION_INTERVAL,
            cookies_path=config.COOKIES_PATH,
        ),
        DriverSettings(),
    )
    logger.info("Instagram instance created")

    instagram_instance.open_url()

    if instagram_instance.accept_cookies()[0]:
        logger.info("Cookies accepted")

    if instagram_instance.login()[0]:
        logger.info("Logged in")
    else:
        logger.error("Cannot login")

    if instagram_instance.disable_notifications()[0]:
        logger.info("Notifications disabled")
    else:
        logger.info(
            "Couldn't disable notifications, probably notifications already disabled or they appear after opening direct"
        )

    if instagram_instance.open_direct()[0]:
        logger.info("Direct opened")
    else:
        logger.warning("Direct couldn't be opened")

    if instagram_instance.disable_notifications()[0]:
        logger.info("Notifications disabled")
    else:
        logger.warning(
            "Couldn't disable notifications, probably notifications already disabled"
        )

    while True:
        if time_send_next_message - time.time() <= 0:
            time_send_next_message = time.time() + random.randint(
                *config.MESSAGGE_SENT_INTERVAL
            )
            try:
                logger.info("Trying to mail vacant person")
                mail_vacant_person(instagram_instance, session)

            except Exception as ex:
                logger.exception(str(ex), stack_info=True)
        if time_next_new_messages_check - time.time() <= 0:
            time_next_new_messages_check = time.time() + random.randint(
                *config.CHECK_FOR_NEW_MESSAGES_INTERVAL
            )
            try:
                logger.info("Trying to check for new messages")
                notify_about_new_messages(instagram_instance, session)

            except Exception as ex:
                logger.exception(str(ex), stack_info=True)

        if time_next_answers_check - time.time() <= 0:
            time_next_answers_check = time.time() + random.randint(
                *config.ANSWERS_CHECK_INTERVAL
            )
            try:
                logger.info("Trying to reply new messages")
                reply_new_messages(instagram_instance, session)

            except Exception as ex:
                logger.exception(str(ex), stack_info=True)
        time.sleep(10)


if __name__ == "__main__":
    main()
