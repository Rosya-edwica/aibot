"""
Модуль, в котором создаются клавиатуры
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from reader import get_categories
import textwrap
import yaml

with open("../config.yml", mode="r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


def get_start_menu() -> ReplyKeyboardMarkup:
    """Возвращает кнопки, заменяющие клавиатуру"""

    menu = ReplyKeyboardMarkup()
    tg_channel_btn = KeyboardButton(text=CONFIG["BUTTONS"]["MESSAGE_ABOUT_CHANNEL"])
    help_btn = KeyboardButton(text=CONFIG["BUTTONS"]["MESSAGE_HELP"])
    main_menu = KeyboardButton(text=CONFIG["BUTTONS"]["MESSAGE_MENU"])
    instruction_btn = KeyboardButton(text=CONFIG["BUTTONS"]["MESSAGE_INSTUCTION"])
    menu.add(tg_channel_btn, main_menu, instruction_btn, help_btn)
    return menu


def get_tg_channel_menu() -> InlineKeyboardMarkup:
    """Возвращает кнопки, относящиеся к информации о канале"""

    menu = InlineKeyboardMarkup()
    url_btn = InlineKeyboardButton(text="Перейти ->", url=CONFIG["CHANNEL_URL"])
    main_menu = InlineKeyboardButton(text="Вернуться на главную", callback_data="main_menu")
    menu.add(url_btn, main_menu)
    return menu


def back_to_menu() -> InlineKeyboardMarkup:
    """Возвращает кнопку, перенаправляющую на главную"""

    menu = InlineKeyboardMarkup()
    main_menu = InlineKeyboardButton(text="Вернуться на главную", callback_data="main_menu")
    menu.add(main_menu)
    return menu


def get_main_menu() -> InlineKeyboardMarkup:
    """Генерирует кнопки категорий"""

    menu = InlineKeyboardMarkup(row_width=2)
    for category in get_categories():
        btn = InlineKeyboardButton(text=textwrap.fill(category), callback_data=f"category_btn_{category}")
        menu.insert(btn)
    return menu

def get_category_item() -> InlineKeyboardMarkup:
    """Возвращает кнопки карточек"""

    menu = InlineKeyboardMarkup(row_width=2)
    main_menu = InlineKeyboardButton("Назад", callback_data="main_menu")
    more_items = InlineKeyboardButton("Еще варианты", callback_data="category_item")

    menu.add(main_menu, more_items)
    return menu