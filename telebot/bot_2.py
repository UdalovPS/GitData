import logging
import os
import requests
import json
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN
from parser import Parser

"""Aiogram objects"""
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class UrlCreator(StatesGroup):
    """This class need for save user steps during choice file"""
    station = State()
    range_time = State()
    files = State()


main_url = "http://212.220.202.105:8080/RINEX/RINEX/2023/"


@dp.message_handler(commands=['date'])
async def choice_date(message: types.Message):
    """This method choice station in list in one day"""
    await message.answer("Send me date")
    await UrlCreator.station.set()


@dp.message_handler(state=UrlCreator.station)
async def choice_station(message: types.Message, state: FSMContext):
    """This method choice station in list in one day"""
    date = int(message.text)

    #parse date urls
    p = Parser(main_url)
    href_dict = p.get_date_href_dict()
    await state.update_data(date_url=href_dict[date])   #save date_url in memory

    #parse station urls
    p = Parser(f"{main_url}{href_dict[date]}")
    station_url = p.get_href_list()

    #create buttons
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for station in station_url:
        keyboard.add(types.KeyboardButton(text=station))
    await message.answer("Выберите станцию", reply_markup=keyboard)
    await UrlCreator.range_time.set()


@dp.message_handler(state=UrlCreator.range_time)
async def choice_station(message: types.Message, state: FSMContext):
    """This method choice range"""
    await state.update_data(station=message.text)
    data = await state.get_data()
    # await message.answer(f"{data['date_url']} -> {data['station']}")
    await message.answer("Напиши диапазон времени по МСК + 2. Например если нужно получить данные с <b>8:00</b> по <b>12:00</b> По МСК то напиши:\n <b>10-14</b>")
    await UrlCreator.files.set()


@dp.message_handler(state=UrlCreator.files)
async def choice_station(message: types.Message, state: FSMContext):
    """This method find files for need time range"""
    data = await state.get_data()       #load data from memory
    time_split_list = message.text.split("-")       #split to START_TIME - END_TIME
    start_time = (datetime.strptime(time_split_list[0], "%H")).time()
    end_time = (datetime.strptime(time_split_list[1], "%H")).time()

    one_day_url = f"{main_url}{data['date_url']}{data['station']}"
    p = Parser(one_day_url)
    one_day_urls_list = p.get_href_list()       #get files url, append in list
    time_obj_list = p.get_datetime()        #get times url, append in list
    time_url_dict = dict(zip(time_obj_list, one_day_urls_list)) #create dict key -> time: value -> file_name
    choice_url_list = [value for key, value in time_url_dict.items() if end_time >= key >= start_time]  #create list with need file

    for file_url in choice_url_list:
        full_url = f"{main_url}{data['date_url']}{data['station']}{file_url}"
        responce = requests.get(url=full_url)
        await bot.send_document(message.chat.id, document=(file_url[:-1], responce.content))
    await state.finish()


@dp.message_handler(commands=['check'])
async def check_working(message: types.Message):
    """This method check bot working"""
    await message.answer('Bot is working')


@dp.message_handler(commands=['load'])
async def check_working(message: types.Message):
    """This method check bot working"""
    file_url = "http://212.220.202.105:8080/RINEX/RINEX/2023/001(0101)/TOUR/TOUR00100_R_20230010000_01H_MN.rnx"
    file_name = 'file.rnx'
    responce = requests.get(url=file_url)
    await bot.send_document(message.chat.id, document=(file_name, responce.content))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
