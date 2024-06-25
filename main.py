import asyncio
from dotenv import dotenv_values

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

bot = Bot(dotenv_values().get('TOKEN'))
dp = Dispatcher()


@dp.message(CommandStart())
@dp.message(F.text.lower().contains('привет'))
async def start(message: Message):
    await message.answer('Приветь^^')


async def main():
    print('Start bot(Ctrl-C for stop)')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop bot')
