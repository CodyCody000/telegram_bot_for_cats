from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
