from aiogram.dispatcher.filters.state import StatesGroup, State

class NotificationBotStates(StatesGroup):
    SendTime = State()
    SendDate = State()
    SendMessage = State()