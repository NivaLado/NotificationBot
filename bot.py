from aiogram import executor
from dispatcher import dp
import handlers
import asyncio

from repository import Repository
Repository = Repository('NotificationBot.db')

DELAY = 60

async def shutdown(dp):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await Repository.close()

def repeat(loop):
    loop.create_task(handlers.controller.broadcaster())
    loop.call_later(DELAY, repeat, loop)

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

if __name__ == "__main__":
    try:
        loop = get_or_create_eventloop()
        ##loop.create_task(handlers.controller.broadcaster())
        loop.call_later(DELAY, repeat, loop)
        executor.start_polling(dp, loop = loop, on_shutdown=shutdown, skip_updates=True)
    except KeyboardInterrupt:
        loop.stop()

