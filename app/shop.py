from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from dotenv import dotenv_values

from database.database import get_user, get_coins_id, set_coins_id
from database.database_shop import (get_list_of_products, get_product,
                                    remove_product, add_product)
from app.keyboards import (generate_markup_list_of_products, shop_markup,
                           question_markup, return_to_list_markup, make_product_accepting,
                           publish_product_markup, return_markup)
from app.filters import (TitleFilter, DescriptionFilter, PriceFilter, state_from_state_group,
                         IsInChatAndChannel, IsNotBanned)
from app.registration import typing

from aiosqlite import Row

ANY_STATE = StateFilter(State(state="*"))
ADMIN_GROUP_ID = dotenv_values().get('ADMIN_GROUP_ID')

shop_router = Router()
shop_router.message.filter(F.chat.type == 'private', IsInChatAndChannel(),
                           IsNotBanned())
shop_group_router = Router()
shop_group_router.message.filter(F.chat.type.in_(['group', 'supergroup']))

# product_id
# title
# description
# author_id
# price

buy_question_state = State('buy_state')
delete_question_state = State('delete_state')


class CreatingProduct(StatesGroup):
    title = State()
    description = State()
    price = State()
    checking = State()


async def generate_text_message(product: Row) -> str:
    author = await get_user(product['author_id'])

    return f'''<b>Название: </b>{html.quote(product['title'])}
<b>Описание: </b>{html.quote(product['description'])}
<b>Автор: </b>@{html.quote(author['username'])}
<b>Цена: </b>{product['price']}'''


async def list_of_user_products(callback: CallbackQuery,
                                current_idx: int = 0):
    list_of_products = await get_list_of_products(callback.message.chat.id)

    try:
        text_messge = await generate_text_message(list_of_products[current_idx])
    except TypeError:
        await callback.message.edit_text('<i>Вы ещё не создали ни одного товара(</i>',
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=return_markup)
        return

    markup_list_of_products = await generate_markup_list_of_products(
        current_idx, list_of_products, from_user=True)

    await callback.message.edit_text(text_messge,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=markup_list_of_products
                                     )


@shop_router.callback_query(F.data.startswith('next_user_'))
async def next_product(callback: CallbackQuery):
    next_idx = int(callback.data.removeprefix('next_user_')) + 1
    await list_of_user_products(callback, next_idx)


@shop_router.callback_query(F.data.startswith('back_user_'))
async def next_product(callback: CallbackQuery):
    next_idx = int(callback.data.removeprefix('back_user_')) - 1
    await list_of_user_products(callback, next_idx)


@shop_router.callback_query(StateFilter(None), F.data.startswith('delete_'))
async def delete_question(callback: CallbackQuery, state: FSMContext):
    await state.update_data(product_id=int(callback.data.removeprefix('delete_')))
    await callback.message.edit_text('Вы точно хотите удалить этот товар?',
                                     reply_markup=question_markup)
    await state.set_state(delete_question_state)


@shop_router.callback_query(delete_question_state, F.data == 'yes')
async def delete_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get('product_id')

    info_of_product = await get_product(product_id)
    title_of_product = info_of_product['title']

    await remove_product(product_id)
    await callback.message.edit_text(f'Вы удалили товар {title_of_product}',
                                     reply_markup=return_to_list_markup)


@shop_router.callback_query(delete_question_state, F.data.in_(['no', 'return_to_list']))
async def return_to_user_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await list_of_user_products(callback)


###############################################################################


async def list_of_products(callback: CallbackQuery,
                           current_idx: int = 0):

    list_of_products = await get_list_of_products()

    try:
        text_messge = await generate_text_message(list_of_products[current_idx])
    except TypeError:
        await callback.message.edit_text('<i>В данный момент отсутствуют какие либо товары(</i>',
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=return_markup)
        return

    markup_list_of_products = await generate_markup_list_of_products(current_idx, list_of_products)

    await callback.message.edit_text(text_messge,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=markup_list_of_products
                                     )


@shop_router.callback_query(F.data.startswith('next_'))
async def next_product(callback: CallbackQuery):
    next_idx = int(callback.data.removeprefix('next_')) + 1
    await list_of_products(callback, next_idx)


@shop_router.callback_query(F.data.startswith('back_'))
async def next_product(callback: CallbackQuery):
    next_idx = int(callback.data.removeprefix('back_')) - 1
    await list_of_products(callback, next_idx)


@shop_router.callback_query(StateFilter(None), F.data == 'return')
@shop_router.callback_query(CreatingProduct.checking, F.data == 'return')
async def return_to_shop_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в раздел с магазинчиком^^ Что вы хотите сделать?',
                                     reply_markup=shop_markup)


@shop_router.callback_query(StateFilter(None), F.data.startswith('buy_'))
async def buy_question(callback: CallbackQuery, state: FSMContext):
    await state.update_data(product_id=int(callback.data.removeprefix('buy_')))
    await callback.message.edit_text('Вы точно хотите купить этот товар?',
                                     reply_markup=question_markup)
    await state.set_state(buy_question_state)


@shop_router.callback_query(buy_question_state, F.data == 'yes')
async def buy_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    data = await state.get_data()
    product_id = data.get('product_id')

    print(user_id)

    coins_of_user = await get_coins_id(user_id)
    info_of_product = await get_product(product_id)
    price_of_product = info_of_product['price']
    title_of_product = info_of_product['title']

    author_of_product = await get_user(info_of_product['author_id'])
    id_author_of_product = author_of_product['user_id']

    if coins_of_user < price_of_product:
        await callback.message.edit_text('У вас недостаточно монеток(',
                                         reply_markup=return_to_list_markup)
        return

    await set_coins_id(coins_of_user-price_of_product, user_id)
    await remove_product(product_id)
    await callback.bot.send_message(id_author_of_product, f'Ваш товар "{title_of_product}" был куплен котиком @{callback.from_user.username}^^')
    await callback.message.edit_text(f'Вы купили товар {title_of_product}^^',
                                     reply_markup=return_to_list_markup)


@shop_router.callback_query(buy_question_state, F.data.in_(['no', 'return_to_list']))
async def return_to_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await list_of_products(callback)

###############################################################################


async def create_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreatingProduct.title)
    await state.update_data(user_id=callback.message.chat.id)
    user_data = await get_user(callback.message.chat.id)
    await state.update_data(username=user_data['username'])
    await callback.message.answer('Напишите название продукта^^')
    await callback.message.answer('Если что, просто пиши "/cancel" для отмены^^')


@shop_router.message(CreatingProduct.title, TitleFilter(30))
async def known_title(message: Message, state: FSMContext):
    await typing(message)
    await state.update_data(title=message.text)
    await message.answer('Таак, теперь описаньице^^')
    await state.set_state(CreatingProduct.description)


@shop_router.message(CreatingProduct.title)
async def known_title_error(message: Message):
    await typing(message)
    await message.answer('Слишком длинное название, прости.‸.')


@shop_router.message(CreatingProduct.description, DescriptionFilter(200))
async def known_title(message: Message, state: FSMContext):
    await typing(message)
    await state.update_data(description=message.text)
    await message.answer('Таак, теперь цену своего товарчика))')
    await state.set_state(CreatingProduct.price)


@shop_router.message(CreatingProduct.description)
async def known_title_error(message: Message):
    await typing(message)
    await message.answer('Блина, я не запомню такое длинное описание... Можно покороче позязя?👉👈')


@shop_router.message(CreatingProduct.price, PriceFilter())
async def known_title(message: Message, state: FSMContext):
    await state.update_data(price=int(message.text))
    await typing(message)
    await message.answer('Оки! Сейчас админчики всё проверят и скажут что и как^^')
    data = await state.get_data()
    await message.bot.send_message(ADMIN_GROUP_ID, f'Админы! Тут котя @{data['username']} хочет свой товар в магазин отправить. Короче:\n \
• Название: {data['title']}\n• Описание: {data['description']}\n• Цена: {data['price']}\n\nПринимаем???',
        reply_markup=await make_product_accepting(data['user_id']))
    await state.set_state(CreatingProduct.checking)


@shop_router.message(CreatingProduct.price)
async def known_title_error(message: Message):
    await typing(message)
    await message.answer('Ты чо так многа просишь?( Ни у кого столько нету((')


@shop_group_router.callback_query(F.data.startswith('product_accepted_'))
async def product_accepted(callback: CallbackQuery):
    user_id = callback.data.removeprefix('product_accepted_')
    await callback.bot.send_message(user_id, 'Еей, товар одобрили^^ Нажми на кнопочку, чтобы опубликовать его^^',
                                    reply_markup=publish_product_markup)
    await callback.message.edit_text('✅', reply_markup=None)
    await callback.answer()


@shop_group_router.callback_query(F.data.startswith('product_rejected_'))
async def product_accepted(callback: CallbackQuery):
    user_id = callback.data.removeprefix('product_rejected_')
    await callback.bot.send_message(user_id, 'Товар отклонили... Нажми кнопку, чтобы вернуться(..',
                                    reply_markup=return_markup)
    await callback.message.edit_text('❎', reply_markup=None)
    await callback.answer()


@shop_router.callback_query(CreatingProduct.checking, F.data == 'publish')
async def publish_product(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await add_product(data['title'], data['description'], data['user_id'], data['price'])
    await callback.message.answer('Товарчик добавлен^^', reply_markup=return_markup)
    await callback.answer()


@shop_router.message(ANY_STATE, Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    if await state_from_state_group(state, CreatingProduct, except_states=['checking']):
        await state.clear()
        await message.answer('Вы вернулись в раздел с магазинчиком^^ Что вы хотите сделать?',
                             reply_markup=shop_markup)


###############################################################################


@shop_router.message(StateFilter(None), Command('shop'))
async def shop(message: Message):
    if await get_user(message.from_user.id) is None:
        await message.answer('Вы не зарегестрированы, для регистрации напишите "/start"^^')
        return
    await message.answer('Вы открыли раздел с магазинчиком^^ Что вы хотите сделать?',
                         reply_markup=shop_markup)


@shop_router.callback_query(StateFilter(None), F.data.startswith('shop__'))
async def shop_action(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    match callback.data.removeprefix('shop__'):
        case 'list_of_products':
            await list_of_products(callback)
        case 'create_product':
            await create_product(callback, state)
        case 'list_of_user_products':
            await list_of_user_products(callback)
        case unknown:
            callback.message.answer(
                f'Непонятненький запрос в магазин( Что такое {unknown}?')
