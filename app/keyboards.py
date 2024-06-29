from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiosqlite import Row

checking_choise_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кружочком', callback_data='video_note')],
    [InlineKeyboardButton(text='Фоточками', callback_data='photoes')]
])

checking_cancel_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
])


async def make_keyboard_accepting(id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да, всё правильно😊',
                              callback_data=f'accepted_{id}')],
        [InlineKeyboardButton(text='Нет, неправильно😠',
                              callback_data=f'rejected_{id}')]
    ])


async def make_profile_markup(id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Открыть профиль :3',
                              callback_data='profile_{id}')]
    ])

shop_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Список товарчиков^^',
                              callback_data='shop__list_of_products')],
        [InlineKeyboardButton(text='Создать товарчик^^',
                              callback_data='shop__create_product')],
        [InlineKeyboardButton(text='Мои товарчики^^',
                              callback_data='shop__list_of_user_products')]
    ]
)

# product_id
# title
# description
# author_id
# price


async def generate_markup_list_of_products(current_idx: int, list_of_products: list[Row]):
    if not (0 <= current_idx < len(list_of_products)):
        raise IndexError('Индекс вышел за границы((')

    current_id_of_product = list_of_products[current_idx]['product_id']
    second_row = []
    if current_idx == len(list_of_products):
        second_row = [InlineKeyboardButton(text=' ')]
    elif current_idx == 0:
        second_row = [InlineKeyboardButton(
            text='Далее ➡', callback_data=f'next_{current_idx}')]
    elif (current_idx + 1) == len(list_of_products):
        second_row = [InlineKeyboardButton(
            text='⬅ Назад', callback_data=f'back_{current_idx}')]
    else:
        second_row = [
            InlineKeyboardButton(text='⬅', callback_data=f'back_{
                                 current_idx}')
        ]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Купить',
                                  callback_data=f'buy_{current_id_of_product}')],
            second_row,
            [InlineKeyboardButton(text='Назад...',
                                  callback_data='return')]]
    )
