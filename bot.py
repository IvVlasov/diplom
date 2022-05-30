from config import dp, bot
import handlers.general
import handlers.admin
# import logging
from aiogram.utils import executor


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
