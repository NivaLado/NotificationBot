import pytz
import datetime
import config
import requests
import asyncio

from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters import Text, Command
from geopy.geocoders import Nominatim
from dispatcher import dp
from dispatcher import log
from aiogram.utils import exceptions
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
            KeyboardButton(text="🗺 Геопозиция", request_location=True),
            KeyboardButton(text="❌ Отмена")
        ]
    ],
    resize_keyboard = True
)

geoBaseUrl = "https://maps.googleapis.com/maps/api/geocode/json?"

# variables
hello = "привет"
unsuccessfulLocationAttempt = """Не удалость определить часовой пояс по локации, попробуйте еще раз либо
🛠 Введите название вашего города или ваш часовой пояс в формате ±ЧЧ:ММ."""

# add new memeber to DB
@dp.message_handler(commands = "start")
async def start(message: Message):
    if(not Repository.userExists(message.from_user.id)):
        Repository.addUser(message.from_user.id, message.chat.id, message.from_user.username)

    await message.bot.send_message(message.from_user.id, "Добро пожаловать!")

# timezone handler
@dp.message_handler(Command("tz"))
async def getTimezone(message: Message):
    timezoneModel = Repository.tryToGetLocationData(message.from_user.id)
    timezoneString = "±0:00"
    if (timezoneModel):
        timezoneString = getWholeTimezone(timezoneModel)

    await message.answer(f"""{timezoneString}
🛠 Введите название вашего города или ваш часовой пояс в формате ±ЧЧ:ММ.
🗺 Или отправьте свою геопозицию.""", reply_markup=keyboard)
    await LocatioQuestionState.SendCountry.set()

# get location
@dp.message_handler(content_types=["location"], state=LocatioQuestionState.SendCountry)
async def location (message: Message, state:FSMContext):
    if message.location is not None:
        timezoneModel = getTimezoneFromLatitudeAndLongitude(message.location.latitude, message.location.longitude)
        Repository.addOrUpdateLocationData(message.from_user.id, message.location.latitude, message.location.longitude, timezoneModel.location, timezoneModel.hours, timezoneModel.minutes)

        result = getWholeTimezone(timezoneModel)

        await state.finish()
        await message.answer(result, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(unsuccessfulLocationAttempt)

# If user has state and want to enter country or time
@dp.message_handler(content_types=['text'], state=LocatioQuestionState.SendCountry)
async def setTimezoneFromCountry(message: Message, state: FSMContext):
    timezoneModel = spacyService.getTimezoneFromString(message.text)
    result = unsuccessfulLocationAttempt
    if (timezoneModel):
        result = getWholeTimezone(timezoneModel)
    elif (False):
        result = ""

    await message.answer(result, reply_markup=ReplyKeyboardRemove())

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

# message handler
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
        spacyService.getDateAndTimeFromString(message.text)
        await message.answer(message.text)

### PRIVATE FUNCTIONS ###
async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await dp.bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcaster():
    try:
        while False:
            await asyncio.sleep(10)
            now = datetime.datetime.utcnow()
            await send_message(391494087, f'{now}')
    finally:
        log.info("messages successful sent.")

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

def getWholeTimezone(timeZone):
    return "🌐 Ваш часовой пояс: GMT" + getHoursFromTimezone(timeZone) + ":" + getMinutesFromTimezone(timeZone) + " " + (timeZone.location or "")

def getHoursFromTimezone(timeZone):
    return "+" + str(timeZone.hours) if timeZone.hours >=0 else str(timeZone.hours)

def getMinutesFromTimezone(timeZone):
    return "00" if timeZone.minutes <= 0 else str(timeZone.minutes)

# isTimezoneSet = Repository.locationDataExists(message.from_user.id)
# Repository.addLocationData(message.from_user.id, message.location.latitude, message.location.longitude, location, hours)

# remove new user joined message
# @dp.message_handler(content_types=["new_chat_members"])
# async def onUserJoined(message: Message):
#     print("JOIN message removed")
#     await message.delete()