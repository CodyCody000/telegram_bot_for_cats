from typing import Any
from aiogram import Bot, html
from aiogram.filters import BaseFilter, CommandObject
from aiogram.types import Message
from aiogram.types import (ChatMemberAdministrator, ChatMemberOwner,
                           ChatMemberMember, ChatMemberLeft, ChatMemberRestricted,
                           ChatMemberBanned, ChatMember)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

from typing import Literal

from database.database import get_max_coins, get_user, get_user_username
from database.database_pool import get_contest_info, get_candidates
from time import time
from dotenv import dotenv_values


class NameFilter(BaseFilter):
    def __init__(self, len_limit):
        self.len_limit = len_limit

    async def __call__(self, message: Message):
        return message.text and len(message.text) <= self.len_limit and message.text[0] != '/'


TitleFilter = DescriptionFilter = NameFilter


class AgeLimit(BaseFilter):
    async def __call__(self, message: Message):
        if message.text and message.text.isdigit():
            return int(message.text) < 18
        return False


class PriceFilter(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        if message.text and message.text.isdigit():
            return int(message.text) <= await get_max_coins()
        return False


class IsRegistrated(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        # print(self.__class__.__name__)
        if message.from_user.is_bot:
            return True

        user_info = await get_user(message.from_user.id)
        if user_info is None:
            await message.reply(
                'Ты не зарегестрирован, для регистрации зайди в лс ботику и напиши "/start"^^')
            return False
        return True


class ContestStarted(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        # print(self.__class__.__name__)
        contest_info = await get_contest_info()
        if contest_info is None:
            await message.reply(
                'Конкурса нет^^ Если хочешь создать свой и если ты админчик, то пиши "/create_contest"^^')
            return False
        return True


class EarlierThan(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        # print(self.__class__.__name__)
        contest_info = await get_contest_info()
        if time() >= contest_info['time_for_candidate']:
            await message.reply(
                'Ты не успел( Жди результатики'
            )
            return False
        return True


class IsNotRegistrated(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        # print(self.__class__.__name__)
        candidates = await get_candidates()
        for candidate in candidates:
            if message.from_user.id == candidate['user_id']:
                await message.answer('Ты уже зарегестрирован в конкурсе^^')
                return False
        return True


class IsInChatAndChannel(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        # print(self.__class__.__name__)
        values = dotenv_values()
        user_id = message.from_user.id
        group_info = await message.bot.get_chat_member(values['CATS_GROUP_ID'], user_id)
        if await self.chat_info_check(group_info):
            channel_info = await message.bot.get_chat_member(values['CATS_CHANNEL_ID'], user_id)
            if await self.chat_info_check(channel_info):
                return True
            else:
                await message.reply('Ты не в канале в данный момент(\nСпроси у админов насчёт этого: @your_lovely_catty и @hooiiiiiii')
        else:
            await message.reply('Ты не в группе в данный момент(\nСпроси у админов насчёт этого: @your_lovely_catty и @hooiiiiiii')
        return False

    async def chat_info_check(self, chat_info: ChatMember) -> bool:
        if isinstance(chat_info, (ChatMemberMember,
                                  ChatMemberAdministrator,
                                  ChatMemberOwner)) or (isinstance(chat_info, ChatMemberRestricted) and chat_info.is_member):
            return True
        return False


class CorrectCommand(BaseFilter):
    async def __call__(self, message: Message, command: CommandObject):
        # print(self.__class__.__name__)
        error_message = f'Ммм... Если что, чтобы командкой воспользоваться, нужно написать \
{html.code(f'/{command.command} @[юзернейм]')} или просто {html.code(f'/{command.command}')}, если отвечаешь на какое нить сообщеньице'

        if message.reply_to_message and command.args:
            await message.reply(error_message, parse_mode=ParseMode.HTML)
            return False
        elif command.args and (not command.args.startswith('@')):
            await message.reply(error_message, parse_mode=ParseMode.HTML)
            return False
        return True


class IsNotBanned(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        # print(self.__class__.__name__)
        user_info = await get_user_username(message.from_user.username)
        if user_info and user_info['is_banned']:
            await message.answer('Ты забанен( Если хочешь разбаниться, пиши админам @your_lovely_catty и @hooiiiiiii')
            return False
        return True


class IsNotMuted(BaseFilter):
    async def __call__(self, message: Message) -> Any:
        # print(self.__class__.__name__)
        user_info = await get_user_username(message.from_user.username)
        if user_info and user_info['is_muted']:
            try:
                await message.delete()
            finally:
                return False
        return True


async def state_from_state_group(state: FSMContext,
                                 state_group: StatesGroup,
                                 except_states: list[str] = None):
    all_states = {s for s in dir(StatesGroup)} - \
        {'get_root'} - set(except_states)
    state_str = await state.get_state()
    return any(state_str.endswith(s) for s in all_states)
