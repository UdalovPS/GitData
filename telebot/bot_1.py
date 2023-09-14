import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import json

from config import TOKEN


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(content_types=['text'])
async def add_note(message: types.Message):
    print('I see')
    text = message.text[:2]
    if text.lower() == '/w':
        url = 'http://localhost:14141/note/'
        data = {
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'note_type': 0,
            'text': message.text[2:]
        }
        response = requests.post(url=url, data=data)
        text = response.json()['text']


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)