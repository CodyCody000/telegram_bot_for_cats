from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from random import choice
from dotenv import dotenv_values

from app.filters import NameFilter, AgeLimit  # type: ignore
from app.keyboards import checking_choise_markup, checking_cancel_markup, make_keyboard_accepting  # type: ignore

hand_emojies = ['👊', '✊', '👌', '☝', '👋',
                '👎', '👍', '👏', '✌', '🖐', '🖖', '🤙', '🤟']

ADMIN_GROUP_ID = dotenv_values().get('ADMIN_GROUP_ID')
photoes = []


class RegistrationStates(StatesGroup):
    name = State()
    age = State()
    task = State()
    video_note = State()
    photoes = State()
    checking = State()


reg_router = Router()
reg_router.message.filter(F.chat.type == 'private')
admin_chat_router = Router()
admin_chat_router.message.filter(F.chat.type.in_(['group', 'supergroup']))


@reg_router.message(StateFilter(None), CommandStart())
@reg_router.message(RegistrationStates.checking, CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(user_id=message.from_user.id)
    await message.answer('Привет! Как к тебе можно обращаться?^^')
    await state.set_state(RegistrationStates.name)


@reg_router.message(RegistrationStates.name, NameFilter(20), F.text)
async def known_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Красивое имя^^ Сколько тебе лет?')
    await state.set_state(RegistrationStates.age)


@reg_router.message(RegistrationStates.name)
async def known_name_error(message: Message):
    await message.answer('Упс, видимо что то не так с твоим имечком^^" Попробуй ещё раз')


@reg_router.message(RegistrationStates.age, AgeLimit(), F.text)
async def known_age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer('Теперь выберите тип проверки, которая нужна, чтобы к нам заходили только дети^^',
                         reply_markup=checking_choise_markup)
    await state.set_state(RegistrationStates.task)


@reg_router.message(RegistrationStates.age)
async def known_age_error(message: Message):
    await message.answer('Какая то ошибочка произошла( Либо тебе 18 или больше, либо ты совсем не число написал. Попробуй ещё раз^^')


@reg_router.callback_query(RegistrationStates.video_note, F.data == 'cancel')
@reg_router.callback_query(RegistrationStates.photoes, F.data == 'cancel')
async def cancelled(callback: CallbackQuery, state: FSMContext):
    global photoes
    photoes.clear()
    await callback.message.answer('Выбери тип проверки, которая нужна, чтобы к нам заходили только дети^^',
                                  reply_markup=checking_choise_markup)
    await state.set_state(RegistrationStates.task)
    await callback.answer()


def generate_video_note_task():
    hand_emojies_set = set()
    while len(hand_emojies_set) < 2:
        hand_emojies_set.add(choice(hand_emojies))
    return 'Запиши кружочек, где ты показываешь грудь и торс (можно и без лица и голоса) \
и последовательно показываешь 2 жеста: {} и {}'.format(*list(hand_emojies_set))


@reg_router.callback_query(RegistrationStates.task, F.data == 'video_note')
async def video_note_task(callback: CallbackQuery, state: FSMContext):
    task = generate_video_note_task()
    await state.update_data(task=task)
    await state.set_state(RegistrationStates.video_note)
    await callback.message.answer(f'Итак, вот твоя задача:\n\n{task}', reply_markup=checking_cancel_markup)
    await callback.answer()


@reg_router.message(RegistrationStates.video_note, F.video_note)
async def video_note_check(message: Message, state: FSMContext):
    await state.set_state(RegistrationStates.checking)
    data = await state.get_data()
    keyboard = await make_keyboard_accepting(data.get('user_id'))
    await message.answer('Оки, сейчас всё проверят и я скажу, нормик или нет^^')
    await message.bot.send_video_note(ADMIN_GROUP_ID, message.video_note.file_id)
    await message.bot.send_message(ADMIN_GROUP_ID, f'Чувачок @{message.from_user.username} сказал, \
что он {data.get('name')}, ему {data.get('age')} и он отправил кружок c таким заданием:\n\n{data.get('task')}\n\nПринимаем???', reply_markup=keyboard)


def generate_photoes_task():
    hand_emojies_set = set()
    while len(hand_emojies_set) < 2:
        hand_emojies_set.add(choice(hand_emojies))
    return 'Скинь 2 фотки. На 1 ты показываешь грудь с этим жестом "{}", на 2 ты показываешь торс с этим жестом "{}"'.format(*list(hand_emojies_set))


@reg_router.callback_query(RegistrationStates.task, F.data == 'photoes')
async def video_note_task(callback: CallbackQuery, state: FSMContext):
    task = generate_photoes_task()
    await state.update_data(task=task)
    await state.set_state(RegistrationStates.photoes)
    await callback.message.answer(f'Итак, вот твоя задача:\n\n{task}', reply_markup=checking_cancel_markup)
    await callback.answer()


@reg_router.message(RegistrationStates.photoes, F.photo)
async def video_note_check(message: Message, state: FSMContext):
    global photoes
    photoes.append(message.photo[-1])
    if len(photoes) == 2:
        local_photoes = photoes.copy()
        photoes.clear()
        await state.set_state(RegistrationStates.checking)
        data = await state.get_data()
        keyboard = await make_keyboard_accepting(data.get('user_id'))
        await message.answer('Оки, сейчас всё проверят и я скажу, нормик или нет^^')
        await message.bot.send_photo(ADMIN_GROUP_ID, local_photoes[0].file_id)
        await message.bot.send_photo(ADMIN_GROUP_ID, local_photoes[1].file_id)
        await message.bot.send_message(ADMIN_GROUP_ID, f'Чувачок @{message.from_user.username} сказал, \
что он {data.get('name')}, ему {data.get('age')} и он отправил фоточки c таким заданием:\n\n{data.get('task')}\n\nПринимаем???', reply_markup=keyboard)


@admin_chat_router.callback_query(F.data.startswith('accepted'))
async def accepted(callback: CallbackQuery):
    user_id = callback.data.split('_')[-1]
    await callback.bot.send_message(user_id, 'Молодец, ты прошёл проверочку! Вот ссылка на наш чатик^^ <типо ссылка>')
    await callback.message.edit_text(text='✅', reply_markup=None)


@admin_chat_router.callback_query(F.data.startswith('rejected'))
async def accepted(callback: CallbackQuery):
    user_id = callback.data.split('_')[-1]
    await callback.bot.send_message(user_id, 'Ты не прошёл проверочку( Напиши /start чтобы начать регистрацию заново')
    await callback.message.edit_text(text='❎', reply_markup=None)


@admin_chat_router.message(CommandStart())
async def admin_start(message: Message):
    await message.answer(f'ID этой группочки^^: {message.chat.id}')
