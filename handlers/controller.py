from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters import Text, Command
import pytz
import datetime

from dispatcher import dp
from bot import Repository
from timezonefinder import TimezoneFinder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

obj = TimezoneFinder(in_memory=True)
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗺 Геопозиция", request_location=True, ),
            KeyboardButton(text="Отмена")
        ]
    ],
    resize_keyboard = True
)

# variables
hello = "привет"

# test command
@dp.message_handler(Command("test"))
async def start(message: Message):
    await message.answer("Test", reply_markup=keyboard)

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
    await message.answer("test", reply_markup=ReplyKeyboardRemove())

# echo
@dp.message_handler()
async def echo(message: Message):
    if (hello in message.text.lower()):
        await message.bot.send_audio(message.chat.id, "http://docs.google.com/uc?export=open&id=1FvXlSh-FmkpktFM8dWo5YMcIR-3RM6Fr")
    else:
        await message.answer(message.text)


### PRIVATE FUNCTIONS ###