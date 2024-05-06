import logging
import os
import requests
from typing import Union
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from parser import Parser

load_dotenv()   # load bot TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


"""Aiogram objects"""
bot = Bot(token=os.getenv('TOKEN_3'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class UrlCreator(StatesGroup):
    """This class need for save user steps during choice file"""
    find_path = State()
    feedback = State()


@dp.callback_query_handler(text="inst")
async def choice_dir_with_inst(callback_query: types.CallbackQuery, state: FSMContext):
    """This method pars data from site and give list dir for choice"""
    p = Parser(url=os.getenv("INSTRUCTION_URL"))
    data = p.get_href_list()
    decode_list = p.get_decode_names_list(encode_list=data)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for directory in decode_list:
        keyboard.add(types.KeyboardButton(text=directory))
    keyboard.add(types.KeyboardButton(text="Не найдено нужное \U0000274C"))
    await callback_query.message.delete()
    await callback_query.message.answer("Выберите тему инструкции", reply_markup=keyboard)
    await state.update_data(url=os.getenv("INSTRUCTION_URL"))
    await UrlCreator.find_path.set()    # set url in memory


@dp.callback_query_handler(text="feedback")
async def request_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer(f"Отправьте отзыв. Что понравилось? Что не понравилось?")
    await UrlCreator.feedback.set()


@dp.message_handler(state=UrlCreator.feedback)
async def send_feedback(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Сохраняю отзыв: {message.text} на сервер")
        requests.post(
            url=f'{os.getenv("SERVER_URL")}/feedback/',
            data={"user_id": message.from_user.id, "text": message.text, "bot_number": 3}
        )
        await message.answer(f"Спасибо за оставленный отзыв")
    except Exception as _ex:
        logger.error(f"Error to save feedback to server: {_ex}")
    finally:
        await state.finish()


@dp.message_handler(state=UrlCreator.find_path)
async def choice_station(message: types.Message, state: FSMContext):
    try:
        if message.text == "Не найдено нужное \U0000274C":
            await state.finish()
            await message.answer(f"Если интересующая инструкция не найдена обратитесь [Поддержку](https://t.me/+USFxg32QN-c0YTZi)", parse_mode="Markdown")
        else:
            memory_data = await state.get_data()       # load data from memory
            p = Parser(url=os.getenv("INSTRUCTION_URL"))

            if message.text == "Назад \U0001F519":
                tmp_list = memory_data["url"].split("/")
                if tmp_list[-1] == "":
                    tmp_list.pop()
                tmp_list.pop()
                url = "/".join(tmp_list) + "/"
            else:
                url = memory_data["url"] + p.get_encode_one_node(node=message.text) + "/"
            check_file = p.check_this_is_file(name=message.text)
            if check_file:
                logger.info(f"File is found to url: {url}")
                await load_and_send_file(message=message, state=state, url=url)
            else:
                logger.info(f"File NOT found to url: {url}")
                p.url = url
                await state.update_data(url=url)
                data = p.get_href_list()
                if not data:
                    raise IndexError("List is empty")
                decode_list = p.get_decode_names_list(encode_list=data)
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                for directory in decode_list:
                    keyboard.add(types.KeyboardButton(text=directory))
                keyboard.add(types.KeyboardButton(text="Назад \U0001F519"))
                keyboard.add(types.KeyboardButton(text="Не найдено нужное \U0000274C"))
                await message.answer("Выберите тему или файл", reply_markup=keyboard)
    except Exception as _ex:
        logger.error(f"Error to get path to file -> {_ex}")
        await state.finish()
        await message.answer(f"Ошибка при поиске инструкции. Обратитесь в [Поддержку](https://t.me/+USFxg32QN-c0YTZi)", parse_mode="Markdown")


async def load_and_send_file(message: types.Message, state: FSMContext, url: str):
    """This method download file and send to client"""
    try:
        file_name = message.text
        logger.info(f"Необходимо скачать файл: {file_name}")
        responce = requests.get(url=url)
        await bot.send_document(message.chat.id, document=(file_name, responce.content))
        requests.post(
            url=f'{os.getenv("SERVER_URL")}/instruction/',
            data={"user_id": message.from_user.id, "file_name": message.text})
    except Exception as _ex:
        logger.error(f"Don't send file. Error -> {_ex}")
        await message.answer(f"Не удалось отправить инструкцию. Обратитесь в [Поддержку](https://t.me/+USFxg32QN-c0YTZi)", parse_mode="Markdown")
    finally:
        await state.finish()


@dp.message_handler(commands=['sup'])
async def check_working(message: types.Message):
    """This method give information about bot commands"""
    reg = await check_registartion(message=message)
    if reg == 3:
        await message.answer("Вы не зарегистрированы. Напишите команду <b>/reg</b> для регистрации")
    if reg == False:
        await message.answer("Ваша заявка еще не одобрена. Обратитесь к [Поддержку](https://t.me/+USFxg32QN-c0YTZi)", parse_mode="Markdown")
    if reg == True:
        text = "Добрый день, вас приветствует виртуальный помощник компании ГД. " \
               "Здесь вы можете скачать инструкции по использованию различного оборудования, " \
               "а так же получить консультационную поддержку от наших технических специалистов."
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="Cкачать инструкции \U0001F4C2", callback_data="inst"))
        keyboard.add(types.InlineKeyboardButton(
            text="Перейти в чат тех.поддержки \U00002753",
            url="https://t.me/+USFxg32QN-c0YTZi")
        )
        keyboard.add(types.InlineKeyboardButton(text="Оценить приложение \U0000270F", callback_data="feedback"))
        await message.answer(text, reply_markup=keyboard)


async def check_registartion(message: types.Message) -> Union[bool, int]:
    """This method check client registration"""
    url = f'{os.getenv("SERVER_URL")}/person/'
    data = {'user_id': message.from_user.id}
    response = requests.get(url=url, data=data)
    logger.info(f"registration client: {message.from_user.id} -> {response.json()['text']}")
    return response.json()['text']


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
            'phone': message.contact.phone_number,
            "bot_number": 3
        }
        url = f'{os.getenv("SERVER_URL")}/person/'
        response = requests.post(url=url, data=data)
        text = response.json()['text']
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(content_types=['text'])
async def check_working(message: types.Message):
    """This method give information about bot commands"""
    text = f"Для того чтобы зарегистрироваться отправьте команду <b>/reg</b>\n" \
           f"Для того чтобы обратиться к виртуальному помощнику отправьте команду <b>/sup</b>"
    await message.answer(text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
