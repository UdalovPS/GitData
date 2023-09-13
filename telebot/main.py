import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import json

from config import TOKEN


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['reg'])
async def registraion_user(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Подать заявку", request_contact=True)
    keyboard.add(button_phone)
    await message.answer("Хотите зарегистрироваться?", reply_markup=keyboard)


@dp.message_handler(content_types=['contact'])
async def contact(message):
    if message.contact is not None:
        data = {
            'user_id': message.contact.user_id,
            'name': message.from_user.username,
            'phone': message.contact.phone_number
        }
        url = 'http://localhost:8000/person/'
        response = requests.post(url=url, data=data)
        text = response.json()['text']
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(content_types=['text'])
async def add_note(message: types.Message):
    text = message.text[:2]
    if text.lower() == '/w':
        url = 'http://localhost:8000/note/'
        data = {
            'user_id': message.from_user.id,
            'note_type': 0,
            'text': message.text[2:]
        }
        response = requests.post(url=url, data=data)
        text = response.json()['text']
        await message.answer(text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
