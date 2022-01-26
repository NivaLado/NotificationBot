from dispatcher import dp
from dispatcher import log

@dp.errors_handler()
async def global_error_handler(update, exception):
    log.exception(f"Error happened! ({exception})")