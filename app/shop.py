from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from database.database import get_user
from database.database_shop import get_list_of_products
from app.keyboards import generate_markup_list_of_products

from aiosqlite import Row

shop_router = Router()
shop_router.message.filter(F.chat.type.is_('private'))

# product_id
# title
# description
# author_id
# price


async def generate_text_message(product: Row) -> str:
    author = await get_user(product['author_id'])

    return f'''<b>Название: </b>{product['title']}
<b>Описание: </b>{product['description']}
<b>Автор: </b>@{author['username']}
<b>Цена: </b>{product['price']}'''


async def list_of_products(callback: CallbackQuery,
                           current_idx: int = 0,
                           list_of_products: list[Row] | None = None) -> None:
    if list_of_products is None:
        list_of_products = await get_list_of_products()

    try:
        text_messge = await generate_text_message(list_of_products[current_idx])
    except IndexError:
        return_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Назад...',
                                                                    callback_data='return')]])
        await callback.message.edit_text('<i>В данный момент отсутствуют какие либо товары(</i>',
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=return_markup)

    markup_list_of_products = await generate_markup_list_of_products(current_idx, list_of_products)

    await callback.message.edit_text(text_messge,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=markup_list_of_products
                                     )


async def create_product(callback: CallbackQuery):
    ...


async def list_of_user_products(callback: CallbackQuery):
    ...
