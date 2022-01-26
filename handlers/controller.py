import sqlite3
import pytz
import datetime as dt
import config
import requests
import asyncio

from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.dispatcher import filters
from aiogram.types import ReplyKeyboardRemove, Message
from geopy.geocoders import Nominatim
from dispatcher import dp
from dispatcher import log
from aiogram.utils import exceptions
from bot import Repository
from timezonefinder import TimezoneFinder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states.locationQuestionState import LocatioQuestionState
from states.notificationBotStates import NotificationBotStates
from models.timezoneModel import TimezoneModel
from services.dateTimeParser import DateTimeParser

obj = TimezoneFinder(in_memory=True)
geolocator = Nominatim(user_agent = "geoapiExercises")
dateTimeParser = DateTimeParser()
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗺 Геопозиция", request_location=True),
            KeyboardButton(text="❌ Отмена")
        ]
    ],
    resize_keyboard = True
)

notificationKeyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ Отмена")
        ]
    ],
    resize_keyboard = True
)

geoBaseUrl = "https://maps.googleapis.com/maps/api/geocode/json?"
hello = "привет"
unsuccessfulLocationAttempt = """Не удалость определить часовой пояс по локации, попробуйте еще раз либо
🛠 Введите название вашего города или ваш часовой пояс в формате ±ЧЧ:ММ."""

schema0 = [["minutes", 10], ["minutes", 5]]
schema1 = [["days", 2], ["minutes", 30], ["minutes", 15]]
schema2 = [["weeks", 1], ["days", 2], ["minutes", 30], ["minutes", 15]]

# add new memeber to DB
@dp.message_handler(commands = "start")
async def start(message: Message):
    if(not Repository.userExists(message.from_user.id)):
        Repository.addUser(message.from_user.id, message.chat.id, message.from_user.username)

    await message.bot.send_message(message.from_user.id, "Добро пожаловать!")

# cancel button
@dp.message_handler(Text(equals=["❌ Отмена"], ignore_case=True), state='*')
async def processButton(message: Message, state:FSMContext):
    await state.finish()
    await message.answer("❌ Отменено", reply_markup=ReplyKeyboardRemove())

# timezone handler
@dp.message_handler(Command("tz"))
async def getTimezone(message: Message, state:FSMContext):
    await state.finish()

    timezoneString = "±0:00"
    timezoneModel = Repository.tryToGetLocationData(message.from_user.id)
    if (timezoneModel):
        timezoneString = getWholeTimezoneMessage(timezoneModel)

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

        result = getWholeTimezoneMessage(timezoneModel)

        await state.finish()
        await message.answer(result, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(unsuccessfulLocationAttempt)

# If user has state and want to enter country or time
@dp.message_handler(content_types=['text'], state=LocatioQuestionState.SendCountry)
async def setTimezoneFromCountry(message: Message, state: FSMContext):
    result = unsuccessfulLocationAttempt

    timezoneModel = dateTimeParser.matchTimezoneFromString(message.text)
    if (timezoneModel):
        result = getWholeTimezoneMessage(timezoneModel)
        Repository.addOrUpdateLocationData(message.from_user.id, timezoneModel.latitude, timezoneModel.longitude, timezoneModel.location, timezoneModel.hours, timezoneModel.minutes)
        await state.finish()
        return await message.answer(result, reply_markup=ReplyKeyboardRemove())

    timezoneModel = await requestTimzoneFromCountryName(message.text)
    if (timezoneModel):
        result = getWholeTimezoneMessage(timezoneModel)
        Repository.addOrUpdateLocationData(message.from_user.id, timezoneModel.latitude, timezoneModel.longitude, timezoneModel.location, timezoneModel.hours, timezoneModel.minutes)
        await state.finish()
        return await message.answer(result, reply_markup=ReplyKeyboardRemove())

    await message.answer(result)

# date command
@dp.message_handler(Command("note"))
async def sendDate(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("Введите время ⏰ 13:15", reply_markup=notificationKeyboard)
    await NotificationBotStates.SendTime.set()

# time handler
@dp.message_handler(content_types=['text'], state=NotificationBotStates.SendTime)
async def sendDate(message: Message, state:FSMContext):
    timeModel = dateTimeParser.matchTimeFromString(message.text)

    if (timeModel):
        await message.answer("""Введите дату 🗓 25/09""")
        await NotificationBotStates.SendDate.set()
        await state.update_data(hours = timeModel.hours, minutes = timeModel.minutes)
    else:
        await message.answer("""Введите время в правильном формате, суки тупые, для кого я эти ебаные часы сюда поставил -> ⏰ 13:15""")


# time handler
@dp.message_handler(content_types=['text'], state=NotificationBotStates.SendDate)
async def sendDate(message: Message, state:FSMContext):
    dateModel = dateTimeParser.matchDateFromString(message.text)

    if (dateModel):
        validatedDate = dateModel.validateDate()

        if not (validatedDate):
            return await message.answer("""Напоминание должно быть в будущем""")

        await message.answer("Введите сообщения о напоминании")
        await NotificationBotStates.SendMessage.set()
        await state.update_data(year = dateModel.year, month = dateModel.month, day = dateModel.day)
    else:
        await message.answer("""Введите дату в формате 🗓 25/09""")


# message handler
@dp.message_handler(content_types=['text'], state=NotificationBotStates.SendMessage)
async def sendDate(message: Message, state:FSMContext):
    async with state.proxy() as data:
        dateTime = dt.datetime(data['year'], data['month'], data['day'], data['hours'], data['minutes'])
        try:
            Repository.addNotification(message.from_user.id, message.chat.id, message.text, dateTime)
            await message.answer(f"Напоминание установлено на: {formatDateTimeAsString(data['year'], data['month'], data['day'], data['hours'], data['minutes'])} {message.text}", reply_markup=ReplyKeyboardRemove())
        except sqlite3.IntegrityError:
            await message.answer(f"Напоминание на это время и дату уже установленно, лошара", reply_markup=ReplyKeyboardRemove())
            
        await state.finish()


@dp.message_handler(Command("list"))
async def sendDate(message: Message, state:FSMContext):
    await state.finish()
    result = Repository.getAllNotificationsByUserId(message.from_user.id)

    if (result):
        resultString = ""
        counter = 0
        for notification in result:
            datetime = dt.datetime.strptime(notification.notificationDateTime, '%Y-%m-%d %H:%M:%S')
            resultString += f"/{counter} {notification.message} : {formatDateTimeAsString(datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute)} \n"
            counter+=1

        await message.answer(resultString)
    else:
        await message.answer("Напоминаний нет")

@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['(\d+)']))
async def send_welcome(message: Message, regexp_command):
    await message.reply("You have requested an item with number: {}".format(regexp_command.group(0)))
    Repository.deleteNotificationByIndex(message.from_user.id ,int(regexp_command.group(0)))

# echo
@dp.message_handler()
async def echo(message: Message):
    if (hello in message.text.lower()):
        await message.bot.send_audio(message.chat.id, "http://docs.google.com/uc?export=open&id=1FvXlSh-FmkpktFM8dWo5YMcIR-3RM6Fr")
    else:
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
    ##try:
        ##while True:
            ##await asyncio.sleep(60)
            await broadCast()

async def broadCast():
    now = dt.datetime.utcnow()
    notificationsGroupedByChatId = Repository.getAllNotifications()

    for groupedNotifications in notificationsGroupedByChatId:
        if groupedNotifications:
            hours = groupedNotifications[0].hours
            hoursAdded = dt.timedelta(hours = hours)
            localizedNow = now + hoursAdded

            for notification in groupedNotifications:
                if notification:
                    notificationTime = dt.datetime.strptime(notification.notificationDateTime, '%Y-%m-%d %H:%M:%S')

                    timeDelta = getTimeDelta(notification.progress)

                    ## Lock notifications in past
                    ## if (notificationTime >= localizedNow):

                    ## Scheduler
                    if (notificationTime - localizedNow <= timeDelta):
                        status = 1 if len(schema0) - 1 <= notification.progress else 0
                        progress = notification.progress + 1
                        Repository.updateNotificationById(notification.id, status, progress)

                        message = f"{notification.message} : " + formatDateTimeAsString(notificationTime.year, notificationTime.month, notificationTime.day, notificationTime.hour, notificationTime.minute)
                        await send_message(notification.chatId, message)

def getTimeDelta(progress):
        if (schema0[progress][0] == "week"):
            return dt.timedelta(weeks = schema0[progress][1])
        if (schema0[progress][0] == "days"):
            return dt.timedelta(weeks = schema0[progress][1])
        if (schema0[progress][0] == "hours"):
            return dt.timedelta(hours = schema0[progress][1])
        if (schema0[progress][0] == "minutes"):
            return dt.timedelta(minutes = schema0[progress][1])



def getTimezoneFromLatitudeAndLongitude(lat, lng):
    timeZone = TimezoneModel()
    timeZone.latitude = lat
    timeZone.longitude = lng
    timeZone.location = obj.timezone_at(lat=lat, lng=lng)
    timezone = pytz.timezone(timeZone.location)
    datetime = dt.datetime.utcnow()
    timeZone.minutes = timezone.utcoffset(datetime).seconds % 60
    timeZone.hours = int((timezone.utcoffset(datetime).seconds - timeZone.minutes) / 60 / 60)
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
        result = getTimezoneFromLatitudeAndLongitude(lat, lng)
        return result
    else:
        return False

def getWholeTimezoneMessage(timeZone):
    return "🌐 Ваш часовой пояс: GMT" + getHoursFromTimezone(timeZone) + ":" + zFillInteger(timeZone.minutes) + " " + (timeZone.location or "")

def getHoursFromTimezone(timeZone):
    sign = ""
    if (timeZone.hours >=0):
        sign = "+"

    hours = zFillInteger(timeZone.hours)

    return sign + hours

def zFillInteger(integer):
    return str(integer).zfill(2)

def formatDateTimeAsString(year, month, day, hours, minutes):
    return f"{zFillInteger(year)}/{zFillInteger(month)}/{zFillInteger(day)} {zFillInteger(hours)}:{zFillInteger(minutes)}"