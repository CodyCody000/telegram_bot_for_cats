from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

rt = Router()


@rt.message(CommandStart())
@rt.message(F.text.lower().contains('привет'))
async def start(message: Message):
    await message.answer('Приветь^^')
