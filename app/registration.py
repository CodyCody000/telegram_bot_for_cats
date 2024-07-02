from aiogram import Router, F, html
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode, ChatAction
from random import choice
from dotenv import dotenv_values
from time import time
from asyncio import sleep
from pprint import pprint

from app.filters import NameFilter, AgeLimit
from app.keyboards import (checking_choise_markup, checking_cancel_markup,
                           make_keyboard_accepting, make_profile_markup,
                           shop_markup)
from app.poll import ContestStates
from database.database import new_user, get_user

hand_emojies = ['👊', '✊', '👌', '☝', '👎', '👍', '✌', '🖐', '🖖', '🤙', '🤟']

ADMIN_GROUP_ID = dotenv_values().get('ADMIN_GROUP_ID')

RULES = f'''{html.bold('Дорогие друзья!🏳️‍🌈')}
{html.italic('🔥Всех приветствую в нашем ламповом gay-чатике🔥')}

{html.bold('👉ПРАВИЛА:👈')}
1.1 Запрещено оскорблять, задевать друг друга - мут/бан.
1.2 Запрещено обсуждать политику - мут.
1.3 Запрещено в любых формах продвигать нацизм, расизм и пр. (стикеры к этому относятся) движения, оскорблять веру - бан.
1.4 Сливать и сохранять фото* участников чата без их согласия - бан.
1.5 Игнорировать требования* админов - мут/бан.
1.6 Обсуждать и продвигать суицидальные мысли*, поддерживать селфхарм*, публиковать фото*, пропагандирующее вышесказанное - мут/бан.
1.7 Неактив >=5 дней и более (без предупреждения и причины) - кик
(можно после заново вступить без проверки, если сохранились доказательства её прохождения.
1.8 Запрещено шутить на любые из вышеуказанных тем.


2.1 Рекламировать сторонние ресурсы*, сайты* и боты* без разрешения админов - варн/мут.
2.2 Спамить* и флудить* - мут/бан.
2.3 Обижаться и расстраиваться - ата-та по попе.

3.1 Запрещено приглашать в чат пользователей*, которые не прошли проверку у админа, переводите всех к одному из админов, они зачтут приглашение - мут/бан/понижение.
3.2 Запрещено накручивать голоса в конкурсных голосованиях*, подкупать, пересылать ссылки на голосования в сторонние группы - дискваликация.
3.3 Запрещено выдавать чужие* фото за свои в чате, использовать фото участников без их согласия - бан.
3.4 Запрещено сливать и сохранять фото* участников* без их разрешения - бан.
3.5 Запрещено отправлять на конкурс чужие фото - бан.
3.6 Запрещен шантаж*, пробив* и спам* участников - бан.

4.1 Запрещено разводить конфликты* среди участников.
4.2 Запрещено скидывать в чат ДП*.

{html.italic('"*" - несет прямое значение ЛЮБЫЕ/ЛЮБОЕ.')}

{html.bold('☠️Незнание правил не освобождает от ответственности. ☠️')}

{html.bold('👉Еще важная информация👈')}
Вы можете искать людей и отправлять им этого бота.
Также пишите, кого привели вы.

{html.bold('🔥За каждые 10 человек вы получаете подарок 🎁🔥')}

{html.bold('❤️‍🔥Уебу кто не прочитает❤️‍🔥')}

{html.bold('Спасибо за внимание!😝')}'''


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


@reg_router.message(F.document)
async def get_photo_id(message: Message):
    pprint(message.document)


async def typing(message: Message):
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await sleep(1.5)


@reg_router.message(RegistrationStates.checking, Command('restart'))
async def restart(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(id=message.from_user.id)
    await start(message, state)


@reg_router.message(StateFilter(ContestStates.registrated, ContestStates.voted), CommandStart())
@reg_router.message(StateFilter(None), CommandStart())
@reg_router.message(RegistrationStates.checking, CommandStart())
async def start(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user(data.get('id'))
    if not user:
        user = await get_user(message.from_user.id)
    print(data.get('id'))
    print(user)
    if user:
        name = user['name']
        coins = user['coins']
        await typing(message)
        await message.answer(f'Приветик, {name}^^\nКоличество монеток: {coins}\nНапиши "/shop", чтобы открыть магазинчик^^')
    elif not (await state.get_state() is None):
        await typing(message)
        await message.answer('Подожди, когда примут заявочку')
        print(await state.get_state())
    else:
        await state.clear()
        await state.update_data(username=message.from_user.username)
        await state.update_data(user_id=message.from_user.id)
        await state.update_data(photoes=[])
        await typing(message)
        await message.answer('''*Ведётся набор в gay\-чатик*🏳️‍🌈

    _В чем плюс?_
    Наш чат небольшой, тут все друг друга знают, ламповое общение и обмены помогут найти друзей💖

    • _Возраст_: до 18 лет🙈
    • _Проверка_: кружок или фото со знаками😳
    • _Конкурс_: имеются🌹
    • _Призы_: естественно💕
    • _Актив и общение_: завались🫣''', parse_mode=ParseMode.MARKDOWN_V2)
        await typing(message)
        await message.answer('Привет! Как к тебе можно обращаться?^^')
        await state.set_state(RegistrationStates.name)


@reg_router.message(RegistrationStates.name, NameFilter(20), F.text)
async def known_name(message: Message, state: FSMContext):
    await typing(message)
    await state.update_data(name=message.text)
    await message.answer('Красивое имя^^ Сколько тебе лет?')
    await state.set_state(RegistrationStates.age)


@reg_router.message(RegistrationStates.name)
async def known_name_error(message: Message):
    await typing(message)
    await message.answer('Упс, видимо что то не так с твоим имечком^^" Попробуй ещё раз')


@reg_router.message(RegistrationStates.age, AgeLimit(), F.text)
async def known_age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await typing(message)
    await message.answer('Теперь выберите тип проверки, которая нужна, чтобы к нам заходили только дети^^',
                         reply_markup=checking_choise_markup)
    await state.set_state(RegistrationStates.task)


@reg_router.message(RegistrationStates.age)
async def known_age_error(message: Message):
    await typing(message)
    await message.answer('Какая то ошибочка произошла( Либо тебе 18 или больше, либо ты совсем не число написал. Попробуй ещё раз^^')


@reg_router.callback_query(RegistrationStates.video_note, F.data == 'cancel')
@reg_router.callback_query(RegistrationStates.photoes, F.data == 'cancel')
async def cancelled(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    data.get('photoes').clear()
    await typing(callback.message)
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
    await typing(callback.message)
    await callback.message.answer(f'Итак, вот твоя задача:\n\n{task}', reply_markup=checking_cancel_markup)
    await callback.answer()


@reg_router.message(RegistrationStates.video_note, F.video_note)
async def video_note_check(message: Message, state: FSMContext):
    await state.set_state(RegistrationStates.checking)
    data = await state.get_data()
    keyboard = await make_keyboard_accepting(data.get('user_id'))
    await typing(message)
    await message.answer('Оки, сейчас всё проверят и я скажу, нормик или нет^^')
    await message.bot.send_video_note(ADMIN_GROUP_ID, message.video_note.file_id)
    await message.bot.send_message(ADMIN_GROUP_ID, f'Чувачок @{message.from_user.username} сказал, \
что он {data.get('name')}, ему {data.get('age')} и он отправил кружок c такой задачей:\n\n{data.get('task')}\n\nПринимаем???', reply_markup=keyboard)


def generate_photoes_task():
    hand_emojies_set = set()
    while len(hand_emojies_set) < 3:
        hand_emojies_set.add(choice(hand_emojies))
    return 'Cкинь 3 фотки с 3 нужными жестами: {}, {}, и {}. Время потрать не больше 10 минут'.format(*list(hand_emojies_set))


@reg_router.callback_query(RegistrationStates.task, F.data == 'photoes')
async def video_note_task(callback: CallbackQuery, state: FSMContext):
    task = generate_photoes_task()
    await state.update_data(task=task)
    await state.update_data(time=time())
    await state.set_state(RegistrationStates.photoes)
    await typing(callback.message)
    await callback.message.answer(f'Итак, вот твоя задача:\n\n{task}', reply_markup=checking_cancel_markup)
    await callback.answer()


@reg_router.message(RegistrationStates.photoes, F.photo)
async def video_note_check(message: Message, state: FSMContext):
    data = await state.get_data()
    if (time() - data.get('time')) <= 600:
        photoes = data.get('photoes')
        photoes.append(message.photo[-1])
        if len(photoes) >= 3:
            local_photoes = photoes.copy()
            photoes.clear()
            await state.set_state(RegistrationStates.checking)
            keyboard = await make_keyboard_accepting(data.get('user_id'))
            await typing(message)
            await message.answer('Оки, сейчас всё проверят и я скажу, нормик или нет^^')
            await message.bot.send_photo(ADMIN_GROUP_ID, local_photoes[0].file_id)
            await message.bot.send_photo(ADMIN_GROUP_ID, local_photoes[1].file_id)
            await message.bot.send_photo(ADMIN_GROUP_ID, local_photoes[2].file_id)
            await message.bot.send_message(ADMIN_GROUP_ID, f'Чувачок @{message.from_user.username} сказал, \
что он {data.get('name')}, ему {data.get('age')} и он отправил фоточки c таким заданием:\n\n{data.get('task')}\n\nПринимаем???', reply_markup=keyboard)
    else:
        await message.answer('Ты не успел( Нажми "Отмена" и попробуй ещё раз', reply_markup=checking_cancel_markup)


@admin_chat_router.callback_query(F.data.startswith('accepted'))
async def accepted(callback: CallbackQuery):
    user_id = callback.data.split('_')[-1]
    await typing(callback.message)
    await callback.bot.send_message(user_id, RULES, parse_mode=ParseMode.HTML)
    await typing(callback.message)
    await callback.bot.send_message(user_id, 'Молодец, ты прошёл проверочку! Вот ссылка на наш чатик^^ <типо ссылка>. Нажми на кнопку внизу, чтобы создать свой профиль^^ Позже, используй "/start" для открытия профиля^^ Также советую ознакомиться с правилами выше, чтобы не получить бан^^',
                                    reply_markup=await make_profile_markup(user_id))
    await callback.message.edit_text(text='✅', reply_markup=None)


@admin_chat_router.callback_query(F.data.startswith('rejected'))
async def accepted(callback: CallbackQuery):
    user_id = callback.data.split('_')[-1]
    await typing(callback.message)
    await callback.bot.send_message(user_id, 'Ты не прошёл проверочку( Напиши /restart чтобы начать регистрацию заново')
    await callback.message.edit_text(text='❎', reply_markup=None)


@reg_router.callback_query(RegistrationStates.checking, F.data.startswith('profile'))
async def profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await new_user(data.get('user_id'), data.get('name'), data.get('username'), data.get('age'))
    await state.clear()
    await state.update_data(id=data.get('user_id'))
    await callback.answer()
    await start(callback.message, state)
