import logging
from aiogram import Bot, Dispatcher, executor, types
import requests

from config import TOKEN


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


TEG_DICT = {
    '/a': 0,
    '/b': 1,
    '/c': 2,
    '/d': 3,
    '/e': 4,
    '/f': 5,
    '/g': 6,
    '/h': 7,
    '/i': 8,
    '/j': 9,
    '/k': 10,
    '/l': 11,
    '/m': 12,
    '/n': 13,
    '/o': 14,
    '/p': 15,
    '/q': 16,
    '/r': 17,
    '/s': 18,
    '/t': 19,
    '/u': 20,
    '/v': 21,
    '/w': 22,
    '/x': 23,
    '/y': 24,
    '/z': 25,
}


@dp.message_handler(content_types=['text'])
async def add_note(message: types.Message):
    print("I see message")
    teg = message.text[:2]
    if teg.lower() in TEG_DICT and message.text[2] == " ":
        url = 'http://localhost:80/note/'
        data = {
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'note_type': TEG_DICT[teg],
            'text': message.text[2:]
        }
        print(data)
        response = requests.post(url=url, data=data)
        text = response.json()['text']


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
