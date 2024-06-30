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

question_markup = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text='Да ✅', callback_data='yes'),
        InlineKeyboardButton(text='Нет ❌', callback_data='no')
    ]]
)

return_to_list_markup = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text='Вернуться к списку',
                             callback_data='return_to_list')
    ]]
)

# product_id
# title
# description
# author_id
# price


async def generate_markup_list_of_products(current_idx: int,
                                           list_of_products: list[Row],
                                           from_user: bool = False):
    if not (list and (0 <= current_idx < len(list_of_products))):
        raise IndexError('Индекс вышел за границы((')

    current_id_of_product = list_of_products[current_idx]['product_id']
    second_row = []
    first_row = []

    if not from_user:
        if len(list_of_products) == 1:
            second_row = []
        elif current_idx == 0:
            second_row = [InlineKeyboardButton(
                text='Далее ➡', callback_data=f'next_{current_idx}')]
        elif (current_idx + 1) == len(list_of_products):
            second_row = [InlineKeyboardButton(
                text='⬅ Назад', callback_data=f'back_{current_idx}')]
        else:
            second_row = [
                InlineKeyboardButton(text='⬅', callback_data=f'back_{
                    current_idx}'),
                InlineKeyboardButton(text='➡', callback_data=f'next_{
                    current_idx}')
            ]

        first_row = [InlineKeyboardButton(
            text='Купить', callback_data=f'buy_{current_id_of_product}')]
    else:
        if len(list_of_products) == 1:
            second_row = []
        elif current_idx == 0:
            second_row = [InlineKeyboardButton(
                text='Далее ➡', callback_data=f'next_user_{current_idx}')]
        elif (current_idx + 1) == len(list_of_products):
            second_row = [InlineKeyboardButton(
                text='⬅ Назад', callback_data=f'back_user_{current_idx}')]
        else:
            second_row = [
                InlineKeyboardButton(text='⬅', callback_data=f'back_user_{
                    current_idx}'),
                InlineKeyboardButton(text='➡', callback_data=f'next_user_{
                    current_idx}')
            ]

        first_row = [InlineKeyboardButton(
            text='Удалить 🗑', callback_data=f'delete_{current_id_of_product}')]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            first_row,
            *[second_row],
            [InlineKeyboardButton(
                text='Назад...', callback_data='return')]]
    )


async def make_product_accepting(id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да, всё правильно😊',
                              callback_data=f'product_accepted_{id}')],
        [InlineKeyboardButton(text='Нет, неправильно😠',
                              callback_data=f'product_rejected_{id}')]
    ])

publish_product_markup = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text='Опубликовать товарчик^^',
                             callback_data='publish')
    ]]
)

return_markup = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Вернуться', callback_data='return')
]])
