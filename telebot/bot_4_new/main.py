import logging
import os
import asyncio
import datetime
import aiohttp
import io
import requests
from typing import Union

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from earthdata import EfemerideDownloadrer
from file_writer import FileWriter

load_dotenv()   # load bot TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN_4")
CMD_1 = "eph1"
CMD_2 = "eph2"
CMD_3 = "eph3"


"""Aiogram objects"""
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


# EFEMERIDE LOGIC
class OneEfemDownload(StatesGroup):
    """This class need for save user steps during choice file"""
    efem_state = State()


class FileCreator(StatesGroup):
    """This class need for save user steps during choice file"""
    project_name_state = State()
    efemeride_state = State()
    excel_state = State()


class FileExcelCreator(StatesGroup):
    """This class need for save user steps during choice file"""
    project_name_state = State()
    excel_state = State()


@dp.message(Command(CMD_1))
async def start_one_efem(message: types.Message, state: FSMContext):
    logger.info(f"Start. Get one emeride file date")
    reg = await check_registartion(message=message)
    if reg == 3:
        await message.answer("Вы не зарегистрированы. Напишите команду <b>/reg</b> для регистрации")
    if reg == False:
        await message.answer("Ваша заявка еще не одобрена. Обратитесь к администрации")
    if reg == True:
        await message.answer("Пришлите дату, на которую нужно выгрузить эфемериды в формате "
                             "<b>YYYY_MM_DD</b>")
        await state.set_state(OneEfemDownload.efem_state)


@dp.message(OneEfemDownload.efem_state)
async def get_efemeride_file(message: types.Message, state: FSMContext):
    logger.info(f"Send date: {message.text}")
    efem_obj = EfemerideDownloadrer(username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))
    datatime_list = efem_obj.get_date_from_str(str_date={message.text})
    if not datatime_list:
        await message.answer("Не корректно введена дата, повторите попытку")
    efemeride_path = efem_obj.get_one_efemeride(str_date_list=datatime_list)
    await bot.send_document(chat_id=message.chat.id, document=types.input_file.FSInputFile(efemeride_path))
    requests.post(
        url=f'{os.getenv("SERVER_URL")}/efemeride/',
        data={"user_id": message.from_user.id, "file_name": efemeride_path.split("/")[-1]}
    )
    await asyncio.sleep(1)
    efem_obj.remove_file(efemeride_path)
    await state.clear()



# DOWNLOAD BY EFEMERIDE LOGIC
@dp.message(Command(CMD_2))
async def start_create_file(message: types.Message, state: FSMContext):
    logger.info(f"Start. Get project name")
    reg = await check_registartion(message=message)
    if reg == 3:
        await message.answer("Вы не зарегистрированы. Напишите команду <b>/reg</b> для регистрации")
    if reg == False:
        await message.answer("Ваша заявка еще не одобрена. Обратитесь к администрации")
    if reg == True:
        await message.answer("Введите название проекта")
        await state.set_state(FileCreator.project_name_state)


@dp.message(FileCreator.project_name_state)
async def get_efemeride_file(message: types.Message, state: FSMContext):
    project_name = f"{message.text}-{datetime.datetime.now().strftime('%d-%B-%Y-%s')}"
    await state.update_data(project_name=project_name)
    obj = FileWriter()
    obj.create_dir(dir_name=project_name)
    obj.copy_files_from_base(target_dir=project_name)
    await message.answer(f"Загрузите файл эфемерид в формате .YYn (Например brdc1640.24n)")
    await state.set_state(FileCreator.efemeride_state)


@dp.message(FileCreator.efemeride_state, F.content_type == types.ContentType.DOCUMENT)
async def get_efemeride_file(message: types.Message, state: FSMContext):
    logger.info(f"IN efemeride state")
    try:
        document = message.document
        logger.info(f"document: {document}")
        # Получаем файл
        file_info = await bot.get_file(document.file_id)
        file_path = file_info.file_path

        efemeride_year = int(document.file_name.split(".")[-1][:2])
        await state.update_data(efemeride_year=efemeride_year)

        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    obj = FileWriter()
                    file_data = await response.read()
                    data = await state.get_data()
                    obj.save_file_in_project_dir(
                        project_name=data["project_name"],
                        file_name=document.file_name,
                        file_data=file_data
                    )
                    await message.answer(f"Загрузите файл  .xlsx")
                    await state.set_state(FileCreator.excel_state)
    except Exception as _ex:
        logger.error(f"Error to process efemeride file -> {_ex}")
        await message.answer(f"Ошибка при обработка эфемерид файла. Повторите отправку")


@dp.message(FileCreator.excel_state)
async def get_excel_file(message: types.Message, state: FSMContext):
    try:
        reg = await check_registartion(message=message)
        if reg == 3:
            await message.answer("Вы не зарегистрированы. Напишите команду <b>/reg</b> для регистрации")
        if reg == False:
            await message.answer("Ваша заявка еще не одобрена. Обратитесь к администрации")
        if reg == True:
            document = message.document

            # Получаем файл
            file_info = await bot.get_file(document.file_id)
            file_path = file_info.file_path
            data = await state.get_data()

            # Скачиваем файл
            file_url = f'https://api.telegram.org/file/bot{os.getenv("TOKEN_4")}/{file_path}'
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        obj = FileWriter()
                        file_data = await response.read()
                        excel_data = io.BytesIO(file_data)
                        # create pandas Dataframe
                        df = obj.read_pandas_from_data(data=excel_data)
                        await message.answer(f"Файлы успешно загружены. Приступаю к формированию отчетов")
                        files_logic = obj.create_all_files(
                            df=df,
                            efemeride_year=data["efemeride_year"],
                            project_name=data["project_name"]
                        )
                        logger.info(f"Answer files logic: {files_logic}")
                        if not files_logic["success"]:
                            await message.answer(files_logic["info"])
                        else:
                            file_paths = obj.get_generate_files_path(project_name=data["project_name"])
                            for file_path in file_paths:
                                await bot.send_document(message.from_user.id, document=types.input_file.FSInputFile(file_path))
                                requests.post(
                                    url=f'{os.getenv("SERVER_URL")}/efemeride/',
                                    data={"user_id": message.from_user.id, "file_name": file_path.split("/")[-1]}
                                )
                            await message.answer("Задача успешно выполнена")
                            await state.clear()
    except Exception as _ex:
        logger.error(f"Error to get excel file -> {_ex}")
        await message.answer("Ошибка при обработке excel файла. Повторите отправку")


# DOWNLOAD BY EXCEL LOGIC
@dp.message(Command(CMD_3))
async def start_excel_logic(message: types.Message, state: FSMContext):
    logger.info(f"Start. Get project name by excel file")
    await message.answer("Введите название проекта")
    await state.set_state(FileExcelCreator.project_name_state)


@dp.message(FileExcelCreator.project_name_state)
async def get_excel_file(message: types.Message, state: FSMContext):
    project_name = f"{message.text}-{datetime.datetime.now().strftime('%d-%B-%Y-%s')}"
    await state.update_data(project_name=project_name)
    obj = FileWriter()
    obj.create_dir(dir_name=project_name)
    obj.copy_files_from_base(target_dir=project_name)
    await message.answer(f"Загрузите файл  .xlsx")
    await state.set_state(FileExcelCreator.excel_state)


@dp.message(FileExcelCreator.excel_state)
async def get_total_files(message: types.Message, state: FSMContext):
    try:
        document = message.document

        # Получаем файл
        file_info = await bot.get_file(document.file_id)
        file_path = file_info.file_path
        data = await state.get_data()

        # Скачиваем файл
        file_url = f'https://api.telegram.org/file/bot{os.getenv("TOKEN_4")}/{file_path}'
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    obj = FileWriter()
                    efem_obj = EfemerideDownloadrer(username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))
                    file_data = await response.read()
                    excel_data = io.BytesIO(file_data)
                    # create pandas Dataframe
                    df = obj.read_pandas_from_data(data=excel_data)
                    date_set = obj.get_date_list(df=df)
                    datetime_list = efem_obj.get_date_from_str(str_date=date_set)
                    await message.answer(f"Идёт загрузка нужных файлов")
                    archives_path = efem_obj.download_archive(str_data_list=datetime_list)
                    await state.clear()
                    await message.answer("Файлы успешно загружены. Приступаю к формированию отчетов")
                    for archive in archives_path:
                        efem_obj.unzip_archive(archive_path=archive, save_path=f"{obj.projects_path}/{data['project_name']}")
                        efem_obj.remove_file(path=archive)
                    files_logic = obj.create_all_files_without_efem(
                        df=df,
                        project_name=data["project_name"]
                    )
                    logger.info(f"Answer files logic: {files_logic}")
                    if not files_logic["success"]:
                        await message.answer(files_logic["info"])
                        await state.clear()
                    else:
                        file_paths = obj.get_generate_files_path(project_name=data["project_name"])
                        for file_path in file_paths:
                            await bot.send_document(message.from_user.id, document=types.input_file.FSInputFile(file_path))
                            requests.post(
                                url=f'{os.getenv("SERVER_URL")}/efemeride/',
                                data={"user_id": message.from_user.id, "file_name": file_path.split("/")[-1]}
                            )
                        await message.answer("Задача успешно выполнена")
                        await state.clear()
    except Exception as _ex:
        logger.error(f"Error to get excel file -> {_ex}")
        await message.answer("Ошибка при обработке excel файла. Повторите отправку")


@dp.message(Command('reg'))
async def registraion_user(message: types.Message):
    if message.from_user.username != None:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Подать заявку 🚩", request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer('Хотите зарегистрироваться? Если да, то нажмите кнопку '
                             '"Подать заявку" ниже', reply_markup=keyboard)
    else:
        await message.answer("У вашего профиля отсутствует <b>Имя пользователя</b>. "
                             "Зайдите в настройки телеграмма и добавьте его.")


@dp.message(F.contact)
async def contact(message):
    if message.contact is not None:
        data = {
            'user_id': message.contact.user_id,
            'name': message.from_user.username,
            'phone': message.contact.phone_number,
            "bot_number": 4
        }
        logger.info(f"{data}")
        url = f'{os.getenv("SERVER_URL")}/person/'
        response = requests.post(url=url, data=data)
        text = response.json()['text']
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text)
async def info_message(message: types.Message):
    await message.answer(
        f"Для того чтобы зарегистрироваться отправьте команду <b>/reg</b>\n"
        f"Напишите команду <b>/{CMD_1}</b> чтобы выгрузить эфемериды (GPS)\n"
        f"Напишите команду <b>/{CMD_2}</b> чтобы выгрузить эфемериды (GPS) вручную\n"
        f"Напишите команду <b>/{CMD_3}</b> чтобы автоматически подгрузить эфемерид (GPS)"
    )


async def check_registartion(message: types.Message) -> Union[bool, int]:
    """This method check client registration"""
    url = f'{os.getenv("SERVER_URL")}/person/'
    data = {'user_id': message.from_user.id}
    response = requests.get(url=url, data=data)
    logger.info(f"registration client: {message.from_user.id} -> {response.json()['text']}")
    return response.json()['text']



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
