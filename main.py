import asyncio
from dotenv import dotenv_values

from aiogram import Bot, Dispatcher
from app.handlers import rt


async def main():
    bot = Bot(dotenv_values().get('TOKEN'))
    dp = Dispatcher()

    dp.include_router(rt)
    print('Start bot(Ctrl-C for stop)')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop bot')
