import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
#from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter
import config

# Configure logging
logging.basicConfig(level=logging.INFO)

# prerequisites
if not config.TOKEN:
    exit("No token provided")

# init
bot = Bot(token=config.TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# activate filters
#dp.filters_factory.bind(IsOwnerFilter)
#dp.filters_factory.bind(IsAdminFilter)
#dp.filters_factory.bind(MemberCanRestrictFilter)