from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Спец символ для админ - панели
spec_simbol = '▶️'

# Доступ к базе postgresql
user = os.getenv('USER_DB')
password = os.getenv('USER_PASS')
database = 'diplom'
host = '127.0.0.1'
port = "5432"
