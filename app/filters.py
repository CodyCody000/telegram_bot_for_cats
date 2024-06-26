from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message


class NameFilter(BaseFilter):
    def __init__(self, len_limit):
        self.len_limit = len_limit

    async def __call__(self, message: Message):
        return message.text and len(message.text) <= self.len_limit and message.text[0] != '/'


class AgeLimit(BaseFilter):
    async def __call__(self, message: Message):
        if message.text and message.text.isdigit():
            return int(message.text) < 18
        return False
