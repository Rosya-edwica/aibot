"""
Модуль для чтения данных из CSV
"""

import csv
import re
from models import NeuroElement

def get_neuro_elements(category: str = None) -> list[NeuroElement]:
    """
    Функция для сбора данных с csv: предполагается, что порядок столбцов не будет меняться
    Возвращает: Список элементов типа NeuroElement, которые включают в себя название, описание, категорию, ссылку
    """

    with open("../data.csv", mode="r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        if category: # Если пользователь выбирает категорию, то выдаем элементы только этой категории
            items = [NeuroElement(*item) for index, item in enumerate(reader) if index != 0 and item[1] == category]
        else: # По дефолту выдаем все элементы
            items = [NeuroElement(*item) for index, item in enumerate(reader) if index != 0]
    return items

def get_categories() -> list[str]:
    """
    Функция для получения категорий без повторений
    Возвращает: список строк
    """

    elements = get_neuro_elements()
    categories = [i.Category for i in elements]
    unique_categories = get_unique_sorted_list(categories)
    return unique_categories

def get_unique_sorted_list(data: list[str]) -> list[str]:
    """
    Функция для получения списка без повторяющихся элементов
    Возвращает: список строк
    """
    unique = []
    for i in data:
        item = re.sub(r"\r|\n", "", i) # убираем из названий категорий такие символы \r \n
        if item not in unique:
            unique.append(item)
    return sorted(unique)
