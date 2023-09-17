import logging
import os

from aiogram import Bot, Dispatcher, executor, types
import requests
import json

from config import TOKEN

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def check_working(message: types.Message):
    """This method check bot working"""
    await message.answer('File is here')


@dp.message_handler(commands=['check'])
async def check_working(message: types.Message):
    """This method check bot working"""
    await message.answer('Bot is working')


@dp.message_handler(commands=['load'])
async def check_working(message: types.Message):
    """This method check bot working"""
    file_url = "http://212.220.202.105:8080/RINEX/RINEX/2023/001(0101)/TOUR/TOUR00100_R_20230010000_01H_MN.rnx"
    server_url = "http://localhost:8000/file/"
    responce = requests.get(url=server_url, params={'url': file_url, 'file_name': "TOUR00100_R_20230010000_01H_MN.rnx"})
    data = responce.json()
    await message.answer('Отправляю файл')
    await bot.send_document(message.chat.id, document=data['file_id'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
