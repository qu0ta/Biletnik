from source.bot_init import dp
from aiogram import executor
from source.handlers import register_handlers

register_handlers(dp)

if __name__ == '__main__':
	executor.start_polling(dp)
