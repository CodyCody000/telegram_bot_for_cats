from typing import Any
from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.database import get_max_coins, get_user


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
        if message.from_user.is_bot:
            return True

        user_info = await get_user(message.from_user.id)
        if user_info is None:
            message.reply(
                'Ты не зарегестрирован, для регистрации зайди в лс ботику и напиши "/start"^^')
            return False
        return True


async def state_from_state_group(state: FSMContext,
                                 state_group: StatesGroup,
                                 except_states: list[str] = None):
    all_states = {s for s in dir(StatesGroup)} - \
        {'get_root'} - set(except_states)
    state_str = await state.get_state()
    return any(state_str.endswith(s) for s in all_states)
