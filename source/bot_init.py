import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
load_dotenv('.env')

TOKEN = "6074365496:AAGlDxcL9F-3nJi2IvLctlA9tY_2WUMjhKM"
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

