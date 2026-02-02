import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота от @BotFather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8530812598:AAHIhDOxmewQe9Rhb4pCkBIhpnDA9FG2edM")

# Ссылки для воронки
CHANNEL_ID = os.getenv("CHANNEL_ID", "@your_free_channel") # Бесплатный канал
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_free_channel")

DIANA_TG = "https://t.me/diana_account" # Личный аккаунт Дианы
VK_REVIEWS = "https://vk.com/your_reviews_page" # ВК с отзывами
PRIVATE_CHANNEL_INFO = "https://t.me/your_bot?start=private" # Ссылка на инфо о приватном канале

# Цены и настройки
PRIVATE_SUBSCRIPTION_PRICE_STARS = 78 # Примерно 3900 руб в звездах (зависит от курса)
DATABASE_URL = "sqlite+aiosqlite:///./numerology.db"