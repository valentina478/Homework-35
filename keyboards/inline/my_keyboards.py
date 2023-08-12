from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from parse.parse import soup

categories = InlineKeyboardButton(text='Категорії', callback_data='categories')
catalog = InlineKeyboardButton(text='Каталог', callback_data='catalog')
all_categories = InlineKeyboardMarkup()
def create_category(w):
    for data in soup.select(w):
        name_category = InlineKeyboardButton(text=data.text.strip(), callback_data=data.text.strip())
        all_categories.add(name_category)
categories_n_catalog = InlineKeyboardMarkup().add(categories, catalog)

all_items = InlineKeyboardMarkup()
def create_item(w):
    for data in soup.select(w):
        name_item = InlineKeyboardButton(text=data.text.strip(), callback_data=data.text.strip())
        all_items.add(name_item)

all_catalog_categories = InlineKeyboardMarkup()
def create_catalog_category(w):
    for data in soup.select(w):
        name_cat_category = InlineKeyboardButton(text=data.text.strip(), callback_data=data.text.strip())
        all_catalog_categories.add(name_cat_category)