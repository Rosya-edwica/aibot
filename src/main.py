from aiogram import Bot, executor, Dispatcher, types
from aiogram.utils import markdown
import markups
from reader import get_neuro_elements
from models import NeuroElement
import yaml


with open("../config.yml", mode="r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

token = CONFIG["TELEGRAM_TOKEN"]
bot = Bot(token)
dp = Dispatcher(bot)

NEURO_GENERATOR = (i for i in get_neuro_elements())

async def set_default_commands(dp: Dispatcher):
    """Функция для создания комманд с описанием (их можно увидеть, если в чате поставить /)"""
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Главное меню"),
    ])

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    """
    Функция, которая срабатывает при отправке команды /start
    Возвращает: главное меню в форме кнопок, заменяющих клавиатуру
    """
    user_name = message.from_user.first_name if message.from_user.first_name != "" else message.from_user.username
    msg = f"Привет, {user_name}!\n{CONFIG['MAIN_MENU']['MESSAGE_WELCOME']}"
    await message.answer(text=msg, reply_markup=markups.get_start_menu())    

@dp.message_handler(text=CONFIG["BUTTONS"]["MESSAGE_ABOUT_CHANNEL"])
async def tg_channel(message: types.Message):
    """
    Функция, которая срабатывает при нажатии на кнопку с текстом из файла config.yml в поле ["BUTTONS"]["MESSAGE_ABOUT_CHANNEL"]
    Функция так же сработает, если написать этот текст вручную
    Возвращает: Текст и привязанную к нему клавиатуру с кнопкой главного меню и ссылкой
    """

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(text=CONFIG["MAIN_MENU"]["MESSAGE_ABOUT_CHANNEL"], reply_markup=markups.get_tg_channel_menu())

@dp.message_handler(text=CONFIG["BUTTONS"]["MESSAGE_INSTUCTION"])
async def instruction_menu(message: types.Message):
    """"
    Функция, которая срабатывает при нажатии на кнопку с текстом из файла config.yml в поле ["BUTTONS"]["MESSAGE_INSTUCTION"]
    Функция так же сработает, если написать этот текст вручную
    Возвращает: Текст с инструкцией и кнопку, которая возвращает к списку кнопок с категориями
    """

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(text=CONFIG["MAIN_MENU"]["MESSAGE_INSTUCTION"], reply_markup=markups.back_to_menu())

@dp.message_handler(text=CONFIG["BUTTONS"]["MESSAGE_HELP"])
async def instruction_menu(message: types.Message):
    """
    Функция, которая срабатывает при нажатии на кнопку с текстом из файла config.yml в поле ["BUTTONS"]["MESSAGE_HELP"]
    Функция так же сработает, если написать этот текст вручную
    Возвращает: Текст с контактами и кнопку, которая возвращает к списку кнопок с категориями
    """

    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(text=CONFIG["MAIN_MENU"]["MESSAGE_HELP"], reply_markup=markups.back_to_menu())


@dp.callback_query_handler(text="main_menu")
async def main_menu(query: types.CallbackQuery):
    """
    Функция, которая срабатывает, если нажать кнопку Вернуться на главную
    Возвращает список кнопок с категориями
    """
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=CONFIG["BUTTONS"]["MESSAGE_MENU"], reply_markup=markups.get_main_menu())

@dp.message_handler(text=CONFIG["BUTTONS"]["MESSAGE_MENU"])
async def main_menu_text(message: types.Message):
    """
    Функция, которая срабатывает, при нажатии на кнопку с текстом из файла config.yml в поле "BUTTONS"]["MESSAGE_MENU"]
    Возвращает список кнопок с категориями
    """
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await bot.send_message(chat_id=message.from_user.id, text=CONFIG["MAIN_MENU"]["MESSAGE_MENU"], reply_markup=markups.get_main_menu())


@dp.callback_query_handler(text_contains="category_btn_")
async def category_item(query: types.CallbackQuery):
    """
    Функция, для обработки всех кнопок категорий
    Функция понимает, какую кнопку нажал пользователь и возвращает ему карточки определенной категории
    """

    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    category = query.data.replace("category_btn_", "") # Получаем название категории с кнопки, которую нажал пользователь

    global NEURO_GENERATOR # Меняем глобальную переменную (знаю, что не лучшее решение)
    NEURO_GENERATOR = (i for i in get_neuro_elements(category)) # Присваиваем глобальной переменной генератор с карточками категории
    text = get_neuro_text() # Берем одну карточку из генератора
    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markups.get_category_item()) # Отправляем карточку

@dp.callback_query_handler(text="category_item")
async def next_category_item(query: types.CallbackQuery):
    """
    Функция, которая срабатывает при нажатии кнопки "Еще варианты"
    Если в генераторе остались карточки, то функция вернет одну карточку
    Если в генераторе карточки закончились, появится сообщение из файла config.yml поля ["MESSAGE_ITEMS_ENDED"] 
    """

    text = get_neuro_text()
    if text is None:
        await bot.send_message(chat_id=query.from_user.id, text=CONFIG["MESSAGE_ITEMS_ENDED"], reply_markup=markups.back_to_menu())
    else:
        await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markups.get_category_item())

def get_neuro_text() -> str | None:
    """
    Функция, которая форматирует карточку
    Если получилось взять карточку, то вернет текст
    Если не получилось, то вернет None
    """

    item = get_next_item()
    if item is None:
        return None
    text = "\n".join((
        f"Название: {item.Name}",
        f"Категория: {item.Category}",
        f"Описание: {item.Description}",
        f"Ссылка: {item.Url}",
    ))
    return text

def get_next_item() -> NeuroElement | None:
    """
    Функция, которая пробует взять следующий элемент генератора
    Если получится, то вернется тип данных NeuroElement
    Если не получится, то вернется None
    """

    try:
        item = next(NEURO_GENERATOR)
    except StopIteration:
        return None
    else:
        return item


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)