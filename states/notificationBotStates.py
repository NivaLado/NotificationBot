from aiogram.dispatcher.filters.state import StatesGroup, State

class NotificationBotStates(StatesGroup):
    SendDate = State()
    SendTime = State()
    SendMessage = State()