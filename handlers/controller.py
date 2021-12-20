from re import T
from aiogram.bot import base
import pytz
import datetime
import config
import requests

from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters import Text, Command
from geopy.geocoders import Nominatim
from dispatcher import dp
from bot import Repository
from timezonefinder import TimezoneFinder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states.locationQuestionState import LocatioQuestionState
from states.notificationBotStates import NotificationBotStates
from models.notificationModel import Notification
from models.timezoneModel import TimezoneModel
from services.spacyNLP import SpacyNLP

obj = TimezoneFinder(in_memory=True)
geolocator = Nominatim(user_agent = "geoapiExercises")
spacyService = SpacyNLP()
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗺 Геопозиция", request_location=True, ),
            KeyboardButton(text="❌ Отмена")
        ]
    ],
    resize_keyboard = True
)

geoBaseUrl = "https://maps.googleapis.com/maps/api/geocode/json?"

# variables
hello = "привет"

# add new memeber to DB
@dp.message_handler(commands = "start")
async def start(message: Message):
    if(not Repository.userExists(message.from_user.id)):
        Repository.addUser(message.from_user.id, message.chat.id, message.from_user.username)

    await message.bot.send_message(message.from_user.id, "Добро пожаловать!")

# timezone handler
@dp.message_handler(Command("tz"), state=None)
async def getTimezone(message: Message):
    await message.answer("""
    🌐 Ваш часовой пояс: GMT±0:00
    🛠 Введите название вашего города или ваш часовой пояс в формате ±ЧЧ:ММ.
    🗺 Или отправьте свою геопозицию.""", reply_markup=keyboard)
    await LocatioQuestionState.SendCountry.set()

# get location
@dp.message_handler(content_types=["location"], state=LocatioQuestionState.SendCountry)
async def location (message: Message, state:FSMContext):
    if message.location is not None:
        timeZone = getTimezoneFromLatitudeAndLongitude(message.location.latitude, message.location.longitude)
        Repository.addOrUpdateLocationData(message.from_user.id, message.location.latitude, message.location.longitude, timeZone.location, timeZone.hours, timeZone.minutes)

        sign = "+" if timeZone.hours >=0 else ""
        minutes = "00" if timeZone.minutes <= 0 else timeZone.minutes
        result = "🌐 Ваш часовой пояс: GMT" + sign + str(timeZone.hours) + ":" + str(minutes)

        await state.finish()
        await message.answer(result, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("""Не удалость определить часовой пояс по локации, попробуйте еще раз либо
        🛠 Введите название вашего города или ваш часовой пояс в формате ±ЧЧ:ММ.""")

# If user has state and want to enter country or time
@dp.message_handler(content_types=['text'], state=LocatioQuestionState.SendCountry)
async def setTimezoneFromCountry(message: Message, state: FSMContext):
    notf = spacyService.getTimezoneFromString(message.text)
    if (notf):
        notf = Notification()
    #time = spacyService.getTimeFromString(message.text)
    await message.bot.send_message(message.from_user.id, "Проверка стейта")
    await message.answer(reply_markup=ReplyKeyboardRemove())

# location button handler
@dp.message_handler(Text(equals=["❌ Отмена"]), state=LocatioQuestionState.SendCountry)
async def processButton(message: Message, state:FSMContext):
    await state.finish()
    await message.answer("❌ Отменено", reply_markup=ReplyKeyboardRemove())

# date command
@dp.message_handler(Command("note"), state=None)
async def sendDate(message: Message):
    await message.answer("""Введите дату""")
    await NotificationBotStates.SendDate.set()

# date handler
@dp.message_handler(content_types=['text'], state=NotificationBotStates.SendDate)
async def sendDate(message: Message, state:FSMContext):
    await message.answer("Введите время")
    await NotificationBotStates.SendTime.set()

# date handler
@dp.message_handler(content_types=['text'], state=NotificationBotStates.SendTime)
async def sendDate(message: Message, state:FSMContext):
    await message.answer("Введите сообщения о напоминании")
    await NotificationBotStates.SendMessage.set()

# date handler
@dp.message_handler(content_types=['text'], state=NotificationBotStates.SendMessage)
async def sendDate(message: Message, state:FSMContext):
    await message.answer("Сообщение введенно")
    state.finish()

# echo
@dp.message_handler()
async def echo(message: Message):
    if (hello in message.text.lower()):
        await message.bot.send_audio(message.chat.id, "http://docs.google.com/uc?export=open&id=1FvXlSh-FmkpktFM8dWo5YMcIR-3RM6Fr")
    else:
        await message.answer(message.text)


### PRIVATE FUNCTIONS ###
def getTimezoneFromLatitudeAndLongitude(lat, lng):
    timeZone = TimezoneModel()
    timeZone.location = obj.timezone_at(lat=lat, lng=lng)
    timezone = pytz.timezone(timeZone.location)
    dt = datetime.datetime.utcnow()
    timeZone.minutes = timezone.utcoffset(dt).seconds % 60
    timeZone.hours = int((timezone.utcoffset(dt).seconds - timeZone.minutes) / 60 / 60)
    return timeZone

async def requestTimzoneFromCountryName(country):
    params = {
        'key': config.GOOGLE_GEOCODIN_API_KEY,
        'address': country
    }

    response = requests.get(geoBaseUrl, params = params).json()
    
    if (response["status"] == "OK"):
        geometry = response["results"][0]["geometry"]
        lat = geometry["location"]["lat"]
        lng = geometry["location"]["lng"]
        result = await getTimezoneFromLatitudeAndLongitude(lat, lng)
        return result
    else:
        return False

# isTimezoneSet = Repository.locationDataExists(message.from_user.id)
# Repository.addLocationData(message.from_user.id, message.location.latitude, message.location.longitude, location, hours)

# remove new user joined message
# @dp.message_handler(content_types=["new_chat_members"])
# async def onUserJoined(message: Message):
#     print("JOIN message removed")
#     await message.delete()