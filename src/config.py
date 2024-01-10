import datetime
import os
import random

# Bot Settings
BOT_NAME = "insta-0"
USE_PROXY = False
PROXY_SERVER_URL = None
SAVE_COOKIES_ON_LOGIN = True
COOKIES_PATH = os.path.join("data", "cookies.pkl")

# Intervals
CHECK_FOR_NEW_MESSAGES_INTERVAL = [400, 600]
PAGE_INTERACTION_INTERVAL = [7, 15]
MESSAGGE_SENT_INTERVAL = [360, 480]
ANSWERS_CHECK_INTERVAL = [30, 40]

ACTIVE_TIME_START = [10, random.randint(11, 49)]
ACTIVE_TIME_END = [20, random.randint(11, 49)]
ACTIVE_TIMEOUT = datetime.datetime(
    year=1, month=1, day=2, hour=ACTIVE_TIME_START[0], minute=ACTIVE_TIME_START[1]
) - datetime.datetime(
    year=1, month=1, day=1, hour=ACTIVE_TIME_END[0], minute=ACTIVE_TIME_END[1]
)

SLEEPING_TIME_DURATION = random.randint(2, 5)
SLEEPING_TIME_START = [
    random.randint(13, 16),
    random.randint(11, 49),
]
SLEEPING_TIME_END = [
    SLEEPING_TIME_START[0] + SLEEPING_TIME_DURATION,
    random.randint(11, 49),
]
# Account

INSTAGRAM_LOGIN = "pasauale2"
INSTAGRAM_PASSWORD = "qyhuZoxUhySu2690"

# EMAIL = "pasquale3456@hotmail.com"
# EMAIL_PASSWORD = "qyhuZoxUhySu2690"

# INSTAGRAM_LOGIN = "brain87949"
# INSTAGRAM_PASSWORD = "Rohizu129"

# EMAIL = "brain7684@hotmail.com"
# EMAIL_PASSWORD = "Rohizu129"


# Database'
DB_USERNAME = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "77.246.101.74"
DB_PORT = "5432"
DB_NAME = "the_club"

# Messages
MESSAGE_TEMPLATES = [
    """$greeting, $first_name! Ваши посты просто поражают своим разнообразием и креативностью. Они словно приносят свежий ветер в мой ленту, делая ее более яркой и интересной. 
Спасибо за ваш талант!""",
    """$greeting, $first_name! Ваши посты просто потрясающие. Они словно оживляют мой ленту, добавляя красок и вдохновения. 
Вы умеете создавать настоящее искусство!""",
    """$greeting, $first_name! Хочу выразить восхищение вашими постами. Они такие разнообразные и интересные, каждый раз удивляют своей оригинальностью. 
Продолжайте радовать нас!""",
    """$greeting, $first_name! Не могу пройти мимо вашей страницы без слов восторга. Ваши посты такие яркие и эмоциональные, словно переносят меня в другой мир. 
Вы просто удивительны!""",
    """$greeting, $first_name! Ваши посты просто завораживают. Они наполнены красотой и гармонией, словно созданы для того, чтобы подарить нам радость. 
Спасибо за ваш талант!""",
]
