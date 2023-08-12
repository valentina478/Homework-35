from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

from transliterate import translit
from loader import dp
from keyboards.inline import create_category, all_categories, categories_n_catalog, create_catalog_category, all_catalog_categories
import requests
from bs4 import BeautifulSoup

site_to_parse = 'https://book-ye.com.ua'
my_answer = requests.get(site_to_parse)
soup = BeautifulSoup(my_answer.content, 'html.parser')

ALL_CATEGORIES = []
for data in soup.select('.header-block.clearfix > p'):
    ALL_CATEGORIES.append(data.text.strip())
ALL_CATALOG_CATEGORIES = []
for data in soup.select('.ctlg-left__item > a'):
    ALL_CATALOG_CATEGORIES.append(data.text.strip())

create_category('.header-block.clearfix > p')
create_catalog_category('.ctlg-left__item > a')

@dp.message_handler(commands='view')
async def view(message: types.Message):
    await message.answer('Оберіть:', reply_markup=categories_n_catalog)

@dp.callback_query_handler(lambda call: 'catalog' in call.data)
async def catalog(call: types.CallbackQuery):
    await call.message.edit_reply_markup(all_catalog_categories)

@dp.callback_query_handler(lambda call: 'categories' in call.data)
async def categories(call: types.CallbackQuery):
    await call.message.edit_reply_markup(all_categories)

items_name_translit = {}
my_link = None
async def my_func_1(path1, path2, path3, call, categories):
    categories_n_links = {}
    category_elements = soup.select(path1)
    link_elements = soup.select(path2)
    for category_data, link_data in zip(category_elements, link_elements):
        category_name = category_data.text.strip()
        category_link = link_data.get('href', '')
        categories_n_links[category_name] = site_to_parse + category_link
    all_items = InlineKeyboardMarkup()
    for cat in categories:
        if cat in call.data:
            for name, link in categories_n_links.items():
                if name == cat:
                    global my_link
                    my_link = link
                    soup_cat = BeautifulSoup(requests.get(my_link).content, 'html.parser')
                    for data in soup_cat.select(path3):
                        title_element = data.find('a', class_='product__media-wrap')
                        if title_element:
                            title_text = title_element.get('title', '').strip()[:64:]
                            callback =  translit(title_text, 'uk', reversed=True)
                            callback = re.sub(r'\W+', ' ', callback).strip().lower()[:64:]
                            item = InlineKeyboardButton(text=title_text, callback_data=callback)
                            all_items.add(item)
                            items_name_translit[title_text] = callback
    await call.message.edit_reply_markup(all_items)

async def my_func_2(call):
    for n, v in items_name_translit.items():
        if call.data == v:
            name = n
            break

    for data in BeautifulSoup(requests.get(my_link).content, 'html.parser').select('.col-xs-6.col-sm-6.col-md-4.col-lg-3.product.product--shadow'):
        title_element = data.find('a', class_='product__media-wrap')
        if title_element:
            title_text = title_element.get('title', '').strip()[:64:]
            if title_text.strip().lower() == name.strip().lower():
                item_link = site_to_parse + title_element.get('href', '')
    item = {}
    item[name] = {}
    soup_item = BeautifulSoup(requests.get(item_link).content, 'html.parser')
    def sort_info(w, enw):
        if w in data.text.strip():
            for e in data.text.strip().split(': ')[-1::]:
                item[name][enw] = e
    for data in soup_item.select('.col-sm-6.card__info'):
        sort_info('Автор', 'author')
        sort_info('Видавництво', 'publisher')
        sort_info('Рік видання', 'copyrightYear')    
        sort_info('Мова', 'language')
        sort_info('Кількість сторінок', 'numberOfPages')
        sort_info('ISBN', 'isbn')
        sort_info('Формат', 'format')
    for data in soup_item.select('.card__price-current'):
        item[name]['price'] = data.text.replace(' ', '')[:9]
    item[name]['image'] = site_to_parse + soup_item.find('img', itemprop='image').get('src')
    for data in soup_item.select('.article > p'):
        about = data.text.strip().replace('\r', '').replace('\t', '').replace('\n', '')
        item[name]['about'] = about
    
    
    my_text = f"""\nВидавництво: {item[name]['publisher']}
Рік видання: {item[name]['copyrightYear']}
Мова: {item[name]['language']}
Кількість сторінок: {item[name]['numberOfPages']}
ISBN: {item[name]['isbn']}
Формат: {item[name]['format']}
Ціна: {item[name]['price']}"""
    
    if 'author' in item[name].keys():
        if item[name]['author']:
            my_text = name + '\nАвтор: ' + item[name]['author'] + my_text
    else:
        my_text = name + my_text
    if item[name]['about']:
        my_text = my_text + f"\nОпис: {item[name]['about']}"
    my_text_end = f"\nФото: {item[name]['image']}\n\nДжерело: {item_link}"
    my_text = my_text + my_text_end
    await call.message.answer(my_text)

@dp.callback_query_handler(lambda call: any(cat in call.data for cat in ALL_CATEGORIES))
async def category_choice(call: types.CallbackQuery):
    await my_func_1('.header-block.clearfix > p', '.header-block__link', '.col-xs-6.col-sm-6.col-md-4.col-lg-3.product.product--shadow', call, ALL_CATEGORIES)

@dp.callback_query_handler(lambda call: any(cat in call.data for cat in ALL_CATALOG_CATEGORIES))
async def catalog_category_choice(call: types.CallbackQuery):
    await my_func_1('.ctlg-left__item > a', '.ctlg-left__link', '.col-xs-6.col-sm-6.col-md-4.col-lg-3.product.product--shadow', call, ALL_CATALOG_CATEGORIES)

@dp.callback_query_handler(lambda call: any(my_translit in call.data for my_translit in items_name_translit.values()))
async def get_catalog_item(call: types.CallbackQuery):
    await my_func_2(call)
