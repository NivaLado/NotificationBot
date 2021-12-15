from aiogram.dispatcher.filters.state import StatesGroup, State

class LocatioQuestionState(StatesGroup):
    SendCountry = State()