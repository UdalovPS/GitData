import logging
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from simple_calendar import calendar_callback, SimpleCalendar

from parser import Parser

load_dotenv()   #load bot TOKEN


"""Aiogram objects"""
bot = Bot(token=os.getenv('TOKEN_2'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class UrlCreator(StatesGroup):
    """This class need for save user steps during choice file"""
    range_time = State()
    files = State()


MAIN_URL = "http://212.220.202.105:8080/RINEX/RINEX/"


@dp.message_handler(commands=['get'])
async def get_calendar(message: types.Message):
    """START calendar method"""
    url = 'http://212.109.197.194:80/person/'
    data = {'user_id': message.from_user.id}
    response = requests.get(url=url, data=data)
    text = response.json()['text']
    if text == 3:
        await message.answer("Вы не зарегистрированы. Напишите команду <b>/reg</b> для регистрации")
    if text == False:
        await message.answer("Ваша заявка еще не одобрена. Обратитесь к администрации")
    if text == True:
        await message.answer("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(calendar_callback.filter())
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:            #if you choice date button
        print(date)
        try:
            await callback_query.message.delete()
            if date.date() > datetime.now().date():
                await callback_query.message.answer(f"Ошибка!!! Выбрана дата из будущего <b>{date.date()}</b>.")
            else:
                year = date.year
                today = (date - datetime(year - 1, 12, 31)).days   #int days about start on the year
                await state.update_data(choice_date=date.date())  #save choice year in memory

                if today == 1:      #if you choice first day in the year
                    yesterday = 365
                    p = Parser(f'{MAIN_URL}{year}/')
                    today_href_dict = p.get_date_href_dict()
                    if today_href_dict == {}:     #user get old year
                        raise ValueError
                    else:
                        today_url = f"{MAIN_URL}{year}/{today_href_dict[today]}"
                    p = Parser(f'{MAIN_URL}{year-1}/')
                    yesterday_href_dict = p.get_date_href_dict()
                    if yesterday_href_dict != {}:
                        yesterday_url = f"{MAIN_URL}{year-1}/{yesterday_href_dict[yesterday]}"
                    else:
                        yesterday_url = None
                else:
                    yesterday = today - 1
                    p = Parser(f'{MAIN_URL}{year}/')
                    href_dict = p.get_date_href_dict()      #scrap data dict with date and date_url
                    if href_dict == {}:     #user get old year
                        raise ValueError
                    today_url = f"{MAIN_URL}{year}/{href_dict[today]}"
                    yesterday_url = f"{MAIN_URL}{year}/{href_dict[yesterday]}"

                await state.update_data(today_url=today_url)        #save today url in memory
                await state.update_data(yesterday_url=yesterday_url)    #save yesteray url in memory

                #parse station URL
                p = Parser(today_url)
                today_station_url = p.get_href_list()
                p = Parser(yesterday_url)
                yesterday_station_url = p.get_href_list()
                for url in yesterday_station_url:       #create common station list from todat and yesterday stations
                    if url not in today_station_url:
                        today_station_url.append(url)

                #create buttons
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                for station in today_station_url:
                    keyboard.add(types.KeyboardButton(text=station[:-1]))
                await callback_query.message.answer("Выберите станцию.", reply_markup=keyboard)
                await UrlCreator.range_time.set()

        except ValueError:
            await callback_query.message.answer("По данному году ничего не найдено.")
        except requests.exceptions.ConnectionError:
            await callback_query.message.answer("Ошибка с соединением сервера. Обратитесь к администрации")


@dp.message_handler(state=UrlCreator.range_time)
async def choice_station(message: types.Message, state: FSMContext):
    """This method choice range"""
    await state.update_data(station=f"{message.text}/")
    await message.answer("Напишите диапазон времени в формате <b>10-12</b>, если вам нужен диапазон данных с <b>10:00</b> до <b>12:00</b> по местному времени Екатеринбург (+5:00).",
                         reply_markup=types.ReplyKeyboardRemove())
    await UrlCreator.files.set()


@dp.message_handler(state=UrlCreator.files)
async def choice_station(message: types.Message, state: FSMContext):
    """This method find files for need time range"""
    data = await state.get_data()       #load data from memory

    try:
        time_split_list = message.text.split("-")       #split to START_TIME - END_TIME
        start_time = (datetime.strptime(time_split_list[0], "%H")).time()
        start_datetime = datetime.combine(data['choice_date'], start_time)

        end_time = (datetime.strptime(time_split_list[1], "%H")).time()
        end_datetime = datetime.combine(data['choice_date'], end_time)

        today_station_url = f"{data['today_url']}{data['station']}"
        p = Parser(today_station_url)
        today_files_url_list = p.get_href_list()        #get files url, append in list
        if today_files_url_list != []:
            time_obj_list = p.get_datetime()                #get times url, append in list
            time_url_tuple = tuple(zip(time_obj_list, today_files_url_list))  #create tuple index 0 -> time: index 1 -> file_name
            today_choice_files = [(value[1], value[0]) for value in time_url_tuple if (value[0] >= start_datetime and value[0] <= end_datetime)]  #create list with need file
        else:
            today_choice_files = ()

        if data['yesterday_url'] == None:
            yesterday_choice_files = ()
        else:
            yesterday_station_url = f"{data['yesterday_url']}{data['station']}"
            p = Parser(yesterday_station_url)
            yesterday_files_url_list = p.get_href_list()        #get files url, append in list
            if yesterday_files_url_list != []:
                time_obj_list = p.get_datetime()                    #get times url, append in list
                time_url_tuple = tuple(zip(time_obj_list, yesterday_files_url_list))  #create tuple index 0 -> time: index 1 -> file_name
                yesterday_choice_files = [(value[1], value[0]) for value in time_url_tuple if (value[0] >= start_datetime and value[0] <= end_datetime)]  #create list with need file
            else:
                yesterday_choice_files = ()

        if today_choice_files == () and yesterday_choice_files == ():
            await message.answer("По текущему времени файлов не найдено.")
            await state.finish()
        else:
            await message.answer(f"Найдено <b>{len(yesterday_choice_files) + len(today_choice_files)}</b> файлов. Дождитесь загрузки.")

            if today_choice_files != ():
                for file_url in today_choice_files:
                    full_url = f"{data['today_url']}{data['station']}{file_url[0]}"
                    responce = requests.get(url=full_url)
                    post_download_statistic(user_id=message.from_user.id, file_name=file_url[0], date=file_url[1])
                    await bot.send_document(message.chat.id, document=(file_url[0], responce.content))

            if yesterday_choice_files != ():
                for file_url in yesterday_choice_files:
                    full_url = f"{data['yesterday_url']}{data['station']}{file_url[0]}"
                    responce = requests.get(url=full_url)
                    post_download_statistic(user_id=message.from_user.id, file_name=file_url[0], date=file_url[1])
                    await bot.send_document(message.chat.id, document=(file_url[0], responce.content))
            await state.finish()
    except Exception as _ex:
        print(f"error to find time interval: {_ex}")
    # except IndexError:
        await message.answer("Не корректно введет временной интервал.")
        await state.finish()

def post_download_statistic(user_id: int, file_name: str, date: datetime):
    url = 'http://212.109.197.194:80/file/'
    data = {
        "user_id": user_id,
        "file_name": file_name,
        "datetime": date,
    }
    requests.post(url=url, data=data)


@dp.message_handler(commands=['check'])
async def check_working(message: types.Message):
    """This method check bot working"""
    await message.answer('Bot is working')


@dp.message_handler(commands=['reg'])
async def registraion_user(message: types.Message):
    if message.from_user.username != None:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Подать заявку", request_contact=True)
        keyboard.add(button_phone)
        await message.answer('Хотите зарегистрироваться? Если да, то нажмите кнопку "Подать заявку" ниже', reply_markup=keyboard)
    else:
        await message.answer("У вашего профиля отсутствует <b>Имя пользователя</b>. Зайдите в настройки телеграмма и добавьте его.")


@dp.message_handler(content_types=['contact'])
async def contact(message):
    if message.contact is not None:
        data = {
            'user_id': message.contact.user_id,
            'name': message.from_user.username,
            'phone': message.contact.phone_number
        }
        url = 'http://212.109.197.194:80/person/'
        response = requests.post(url=url, data=data)
        text = response.json()['text']
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(content_types=['text'])
async def check_working(message: types.Message):
    """This method give information about bot commands"""
    text = f"Для того чтобы зарегистрироваться отправьте команду <b>/reg</b>\n" \
           f"Для того чтобы скачать информацию по станциям отправьте команду <b>/get</b>"
    await message.answer(text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
