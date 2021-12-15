from aiogram.bot import base
import pytz
import datetime
import geocoder
import config
import requests
from tzlocal import get_localzone



from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters import Text, Command
from geopy.geocoders import Nominatim
from dispatcher import dp
from bot import Repository
from timezonefinder import TimezoneFinder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states.locationQuestionState import LocatioQuestionState

obj = TimezoneFinder(in_memory=True)
geolocator = Nominatim(user_agent = "geoapiExercises")
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗺 Геопозиция", request_location=True, ),
            KeyboardButton(text="Отмена")
        ]
    ],
    resize_keyboard = True
)

geoBaseUrl = "https://maps.googleapis.com/maps/api/geocode/json?"

# variables
hello = "привет"

# test command
@dp.message_handler(Command("test"), state=None)
async def start(message: Message):
    await message.answer("Test", reply_markup=keyboard)
    await LocatioQuestionState.SendCountry.set()

# If user has state and want to enter country
@dp.message_handler(state=LocatioQuestionState.SendCountry)
async def setTimezoneFromCountry(message: Message, state: FSMContext):
    country = message.text
    timezones = pytz.country_timezones(message.text)
    if not len(timezones):
            await message.answer(
                "{} does not appear to be a "
                "valid ISO 3166 country code.".format(country))
            return
    name = pytz.country_names[country]
    await message.answer(
            "Commonly used timezones in {}: {}.".format(
                name, ", ".join(timezones))) 
    await message.bot.send_message(message.from_user.id, "Проверка стейта")


# add new memeber to DB
@dp.message_handler(commands = "start")
async def start(message: Message):
    if(not Repository.userExists(message.from_user.id)):
        Repository.addUser(message.from_user.id)

    await message.bot.send_message(message.from_user.id, "Добро пожаловать!")

# get location
@dp.message_handler(content_types=["location"])
async def location (message):
    if message.location is not None:
        location = obj.timezone_at(lat=message.location.latitude, lng=message.location.longitude)
        timezone = pytz.timezone(location)
        dt = datetime.datetime.utcnow()
        hours = timezone.utcoffset(dt).seconds / 60 / 60
        Repository.addLocationData(message.from_user.id, message.location.latitude, message.location.longitude, location, hours)
        Repository.updateLocationData(message.from_user.id, message.location.latitude, message.location.longitude, location, hours)
        isTimezoneSet = Repository.locationDataExists(message.from_user.id)
        sign = "+" if hours >=0 else "-"
        result = "🌐 Ваш часовой пояс: GMT" + sign + " " + str(hours) + ":00"
        await message.answer(result, reply_markup=ReplyKeyboardRemove())

# remove new user joined message
@dp.message_handler(content_types=["new_chat_members"])
async def onUserJoined(message: Message):
    print("JOIN message removed")
    await message.delete()

# location button handler
@dp.message_handler(Text(equals=["Отмена"]))
async def processButton(message: Message):
    await message.answer("Отмена", reply_markup=ReplyKeyboardRemove())

# echo
@dp.message_handler()
async def echo(message: Message):
    params = {
        'key': config.GOOGLE_GEOCODIN_API_KEY,
        'address': "Riga"
    }

    response = requests.get(geoBaseUrl, params = params).json()
    
    if (response["status"] == "OK"):
        geometry = response["results"][0]["geometry"]
        lat = geometry["location"]["lat"]
        lng = geometry["location"]["lng"]
        result = getTimezoneFromLatitudeAndLongitude(lat, lng)

    # location = geolocator.geocode(message.text)
    # loc_dict = location.raw
    # country = loc_dict['display_name'].rsplit(',' , 1)[1].strip()

    # result = pytz.timezone(country + "/" + "Riga")

    # if (hello in message.text.lower()):
    #     await message.bot.send_audio(message.chat.id, "http://docs.google.com/uc?export=open&id=1FvXlSh-FmkpktFM8dWo5YMcIR-3RM6Fr")
    # else:
    #     await message.answer(message.text)


### PRIVATE FUNCTIONS ###
async def getTimezoneFromLatitudeAndLongitude(lat, lng):
    location = obj.timezone_at(lat=lat, lng=lng)
    timezone = pytz.timezone(location)
    dt = datetime.datetime.utcnow()
    hours = timezone.utcoffset(dt).seconds / 60 / 60
    return hours


async def function(message: Message):
    await message.bot.send_message(message.chat.id, "So, I'm answering to his username at this point: {}".format(message.text))