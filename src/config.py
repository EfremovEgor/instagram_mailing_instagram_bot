import os

# Bot Settings
BOT_NAME = "insta-0"
USE_PROXY = False
PROXY_SERVER_URL = None
SAVE_COOKIES_ON_LOGIN = True
COOKIES_PATH = os.path.join("data", "cookies.pkl")

# Intervals time_next_login_check
CHECK_FOR_NEW_MESSAGES_INTERVAL = [400, 600]
PAGE_INTERACTION_INTERVAL = [7, 15]
MESSAGGE_SENT_INTERVAL = [360, 480]
ANSWERS_CHECK_INTERVAL = [30, 40]
LOGIN_CHECK_INTERVAL = [600, 720]

# Account

# INSTAGRAM_LOGIN = "pasauale2"
# INSTAGRAM_PASSWORD = "qyhuZoxUhySu2690"

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
