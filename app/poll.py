from dataclasses import dataclass
from aiogram import Router, F, html, Bot
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner, Poll
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode
import asyncio

from aiosqlite import Row
from dotenv import dotenv_values
from time import time

from app.filters import IsRegistrated, ContestStarted, EarlierThan
from database.database_pool import (get_contest_info, write_row_in_database,
                                    get_candidates, clear_contest,
                                    get_candidate, incriment_candidate)
from database.database import get_user, get_coins_id, set_coins_id


class ContestStates(StatesGroup):
    choising_contest = State()
    task_for_contest = State()
    price_of_contest = State()
#   ...
    sending_candidate = State()
    registrated = State()
    voted = State()


@dataclass
class Contest:
    repr: str
    user_friendly: str
    type_of_candidate: str
    task: str
    price: int = 0
    time_for_candidates: int = 24*60*60
    time_for_poll: int = 24*60*60


TYPE_OF_POLL = {
    'Конкурс тест': Contest('test_contest', 'Конкурс тест', 'photo',
                            'Тест конкурсов'),
    'Конкурс членов': Contest('dick_contest', 'Конкурс членов', 'photo',
                              'Участники скидывают фото своих членов и одним голосованием выбирается победитель!',
                              time_for_candidates=3*60,
                              time_for_poll=2*60),
    'Конкурс фото (18+)': Contest('photo_contest_18_plus', 'Конкурс фото (18+)', 'photo',
                                  'Участники скидывают свои 18+ фото и одним голосованием выбирается победитель!'),
    'Конкурс стонов': Contest('moan_contest', 'Конкурс стонов', 'voice',
                              'Участники скидывают голосовое со своими стонами, одним голосованием выбирается победитель!'),
    'Конкурс ножек': Contest('legs_contest', 'Конкурс ножек', 'photo',
                             'Участники скидывают свои прекрасные ножки, победителей выбирают одним голосованием!'),
    'Конкурс пошлых историй': Contest('vulgar_story_contest', 'Конкурс пошлых историй', 'text',
                                      'Участники пишут любые 18+ историю в любом жанре (вирт, фанфик, рассказ и т.д.) и они публикуются в канале, а потом голосованием выбирается лучшаяя'),
    'Конкурс фото (любых)': Contest('photo_contest_any', 'Конкурс фото (любых)', 'photo',
                                    'Участники скидывают любые свои фотографии, необязательно 18+, но на них обязательно должен быть изображён участник, (присылать чужие фото запрещено, см. правила). Голосованием выбирается самое классное фото.'),
    'Конкурс рабов': Contest('slave_contest', 'Конкурс рабов', 'video',
                             'Мальчики, которые хотят повыполнять задания получают специальный список заданий, сформированный другими участниками, выполняют их с отчетами и отсылают в бота одним видео, участники выбирают самого послушного и красивого.')
}

TYPE_OF_POLL_REPR = {
    'test_contest': Contest('test_contest', 'Конкурс тест', 'photo',
                            'Тест конкурсов', time_for_candidates=3*60, time_for_poll=2*60),
    'dick_contest': Contest('dick_contest', 'Конкурс членов', 'photo',
                            'Участники скидывают фото своих членов и одним голосованием выбирается победитель!'),
    'photo_contest_18_plus': Contest('photo_contest_18_plus', 'Конкурс фото (18+)', 'photo',
                                     'Участники скидывают свои 18+ фото и одним голосованием выбирается победитель!'),
    'moan_contest': Contest('moan_contest', 'Конкурс стонов', 'voice',
                            'Участники скидывают голосовое со своими стонами, одним голосованием выбирается победитель!'),
    'legs_contest': Contest('legs_contest', 'Конкурс ножек', 'photo',
                            'Участники скидывают свои прекрасные ножки, победителей выбирают одним голосованием!'),
    'vulgar_story_contest': Contest('vulgar_story_contest', 'Конкурс пошлых историй', 'text',
                                    'Участники пишут любые 18+ историю в любом жанре (вирт, фанфик, рассказ и т.д.) и они публикуются в канале, а потом голосованием выбирается лучшаяя'),
    'photo_contest_any': Contest('photo_contest_any', 'Конкурс фото (любых)', 'photo',
                                 'Участники скидывают любые свои фотографии, необязательно 18+, но на них обязательно должен быть изображён участник, (присылать чужие фото запрещено, см. правила). Голосованием выбирается самое классное фото.'),
    'slave_contest': Contest('slave_contest', 'Конкурс рабов', 'video',
                             'Мальчики, которые хотят повыполнять задания получают специальный список заданий, сформированный другими участниками, выполняют их с отчетами и отсылают в бота одним видео, участники выбирают самого послушного и красивого.')
}

dotenv_values = dotenv_values()

# Поменяй потом!!
CHANNEL_ID = dotenv_values['CATS_CHANNEL_ID']
GROUP_ID = dotenv_values['CATS_GROUP_ID']

TIME_FOR_CANDIDATES = [[0]]

poll_private_router = Router()
poll_private_router.message.filter(F.chat.type == 'private',
                                   IsRegistrated())

poll_channel_router = Router()
poll_channel_router.poll_answer.filter(F.chat.type == 'channel')


async def is_admin(message: Message):
    user_in_chat_info = await message.bot.get_chat_member(GROUP_ID,
                                                          message.from_user.id)
    return isinstance(user_in_chat_info, (ChatMemberAdministrator, ChatMemberOwner))


@poll_private_router.message(StateFilter(None), Command('create_contest'))
async def create_contest(message: Message, state: FSMContext):
    if not (await is_admin(message)):
        await message.answer('Ты не админ к сожалению(((')
        return

    contest_info = await get_contest_info()
    if contest_info is not None:
        print(contest_info)
        user_info = await get_user(contest_info['user_id'])
        await message.answer(f'Извини, но в данный момент уже действует другой конкурс от {user_info['name']}(')
        return

    await state.update_data(creator_id=message.from_user.id)
    await state.update_data(creator_username=message.from_user.username)

    builder = ReplyKeyboardBuilder()
    for poll in TYPE_OF_POLL:
        builder.button(text=poll)

    await state.set_state(ContestStates.choising_contest)
    await message.answer('Выбери тип конкурса^^',
                         reply_markup=builder.adjust(2).as_markup(resize_keyboard=True,
                                                                  one_time_keyboard=True))


@poll_private_router.message(ContestStates.choising_contest, F.text)
async def context_chosed(message: Message, state: FSMContext):
    if message.text in TYPE_OF_POLL:
        await state.update_data(name=TYPE_OF_POLL[message.text].repr)
        await state.update_data(name_for_users=TYPE_OF_POLL[message.text].user_friendly)
        if message.text == 'Конкурс рабов':
            await message.answer('Напиши задания для конкурся рабов^^')
            await state.set_state(ContestStates.task_for_contest)
        else:
            await state.update_data(task='')
            await message.answer('Напиши банк для конкурса^^')
            await state.set_state(ContestStates.price_of_contest)


@poll_private_router.message(ContestStates.task_for_contest, F.text)
async def task_for_contest_writen(message: Message, state: FSMContext):
    await state.update_data(task=message.text)
    await message.answer('Оки, теперь напиши банк для конкурса^^')
    await state.set_state(ContestStates.price_of_contest)


@poll_private_router.message(ContestStates.price_of_contest, F.text)
async def price_of_contest_writen(message: Message, state: FSMContext):
    global TIME_FOR_CANDIDATES
    if not message.text.isdigit():
        await message.answer('Это не число( Напиши число')
        return

    await state.update_data(price=int(message.text))
    state_data = await state.get_data()
    await state.clear()
    poll_data = TYPE_OF_POLL_REPR[state_data['name']]
    await write_row_in_database(state_data['creator_id'], state_data['name'],
                                state_data['task'], state_data['price'],
                                poll_data.time_for_candidates+time(),
                                poll_data.time_for_candidates+poll_data.time_for_poll+time(),
                                'creator')
    await message.answer('Конкурс был создан^^')
    await message.bot.send_message(GROUP_ID, f'''{html.bold('Был открыт конкурс!!!')}
• Создатель: {state_data['creator_username']}
• Тип конкурса: {state_data['name_for_users']}
• Банк: {state_data['price']}

Чтобы поучаствовать, пиши в лс боту "{html.code('/participate')}"^^''', parse_mode=ParseMode.HTML)
    print(TIME_FOR_CANDIDATES[0][0])
    await make_poll(message.bot, poll_data)


async def make_poll(bot: Bot, poll_data: Contest):
    await asyncio.sleep(poll_data.time_for_candidates)
    all_candidates = await get_candidates()
    if len(all_candidates) == 0:
        await bot.send_message(GROUP_ID, 'Никому не интересен конкурс(((')
        await clear_contest()
        return
    elif len(all_candidates) == 1:
        await register_winners(bot, all_candidates)
        return
    else:
        for i, row in enumerate(all_candidates, 1):
            match poll_data.type_of_candidate:
                case 'video':
                    await bot.send_video(CHANNEL_ID, row['data'],
                                         caption=f'Кандидат {i}: {row['name']}')
                case 'text':
                    await bot.send_message(CHANNEL_ID,
                                           f'Кандидат {i} - {row['name']}:\n\n{row['data']}')
                case 'photo':
                    await bot.send_photo(CHANNEL_ID, row['data'],
                                         caption=f'Кандидат {i}: {row['name']}')
                case 'voice':
                    await bot.send_voice(CHANNEL_ID, row['data'],
                                         caption=f'Кандидат {i}: {row['name']}')
    await bot.send_message(CHANNEL_ID, f'Чтобы проголосовать за кандидата, напиши в лс ботику {
        html.code('/vote [Имя кандидата]')}',
        parse_mode=ParseMode.HTML)
    await asyncio.sleep(poll_data.time_for_poll)
    await register_winners(bot)


@poll_private_router.message(StateFilter(None), Command('participate'),
                             ContestStarted(), EarlierThan())
async def participate(message: Message, state: FSMContext):
    user_info = await get_user(message.from_user.id)
    await state.update_data(name=user_info['name'])
    contest_info = await get_contest_info()
    contest = TYPE_OF_POLL_REPR[contest_info['name']]
    await state.update_data(contest=contest)
    await message.answer(f'''Привет! Вот правила для этого конкурса^^:

{contest.task}''')
    if contest.repr == 'slave_contest':
        await message.answer(f'''Задание для рабов^^:

{contest_info['data']}''')

    await state.set_state(ContestStates.sending_candidate)


@poll_private_router.message(ContestStates.sending_candidate)
async def sended_candidate(message: Message, state: FSMContext):
    state_data = await state.get_data()
    contest: Contest = state_data['contest']
    print(contest.type_of_candidate)
    flag = True
    if (contest.type_of_candidate == 'video') and message.video:
        await write_row_in_database(message.from_user.id, state_data['name'],
                                    message.video.file_id, 0)
    elif (contest.type_of_candidate == 'photo') and message.photo:
        await write_row_in_database(message.from_user.id, state_data['name'],
                                    message.photo[0].file_id, 0)
    elif (contest.type_of_candidate == 'voice') and message.voice:
        await write_row_in_database(message.from_user.id, state_data['name'],
                                    message.voice.file_id, 0)
    elif (contest.type_of_candidate == 'text') and message.text:
        await write_row_in_database(message.from_user.id, state_data['name'],
                                    message.text, 0)
    else:
        flag = False

    if flag:
        await state.clear()
        await message.answer('Заявка принята^^ Жди результатики^^')
        await state.set_state(ContestStates.registrated)
        await clear_state_after_contest(state)


async def get_winners(candidates: list[Row]):
    max_vote = 0
    winners = []
    for candidate in candidates:
        if candidate['num_of_votes'] > max_vote:
            max_vote = candidate['num_of_votes']
            winners = [candidate]
        elif candidate['num_of_votes'] == max_vote:
            winners.append(candidate)
    return winners


async def register_winners(bot: Bot, winners: list[Row] | None = None):
    global TIME_FOR_CANDIDATES
    if winners is None:
        candidates = await get_candidates()
        winners = await get_winners(candidates)
    await bot.send_message(GROUP_ID, f'Вот и победител{'и' if len(winners) > 1 else 'ь'} нашего конкурса: \
{', '.join(winner['name'] for winner in winners)}. Поздравляем {'их' if len(winners) > 1 else 'его'}^^')
    for winner in winners:
        coins = await get_coins_id(winner['user_id'])
        contest_info = await get_contest_info()
        await set_coins_id(contest_info['price']//len(winners) + coins,
                           winner['user_id'])
    print('register_winners')
    TIME_FOR_CANDIDATES[0][0] = 0
    await clear_contest()


@poll_private_router.message(Command('vote'), ContestStarted(),
                             IsRegistrated())
async def vote(message: Message, state: FSMContext, command: CommandObject):
    state_name = await state.get_state()
    if state_name.endswith('voted'):
        await message.answer('Ты уже проголосовал^^')
        return
    if not command.args:
        await message.answer('Неверная команда, посмотри в канальчике как она делается^^')
        return
    candidate_name = command.args
    candidate = await get_candidate(candidate_name)
    if candidate is None:
        await message.answer('Такой человечек у нас не участвует(')
        return
    if message.from_user.id == candidate['user_id']:
        await message.answer('Не интересно за самого себя голосовать(')
        return
    await incriment_candidate(candidate['name'])
    await write_row_in_database(message.from_user.id, f'voter_{message.from_user.id}', candidate_name,
                                0, candidate_type='voter')
    await state.set_state(ContestStates.voted)
    await message.answer('Голос принят^^')
    await clear_state_after_contest_for_voters(state)


async def clear_state_after_contest(state: FSMContext):
    context_info = await get_contest_info()
    await asyncio.sleep(context_info['time_for_candidate']-time())
    await state.clear()


async def clear_state_after_contest_for_voters(state: FSMContext):
    context_info = await get_contest_info()
    await asyncio.sleep(context_info['time_for_poll']-time())
    await state.clear()
