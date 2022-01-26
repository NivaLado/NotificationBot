import logging
import config
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Configure logging
logging.basicConfig(filename='notifications.log', encoding='utf-8', level=logging.INFO)
log = logging.getLogger('notifications')

# prerequisites
if not config.TOKEN:
    exit("No token provided")

# init
bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())