import asyncio
from dotenv import dotenv_values

<<<<<<< HEAD
from aiogram import Bot, Dispatcher
from app.handlers import rt  # type: ignore
from database.database import init  # type: ignore
=======
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.registration import reg_router, admin_chat_router
>>>>>>> 81e2d93 (Base functional for registration)


async def main():
    bot = Bot(dotenv_values().get('TOKEN'))
    dp = Dispatcher()
<<<<<<< HEAD

    init()

    dp.include_router(rt)
=======
    dp.include_routers(reg_router, admin_chat_router)
>>>>>>> 81e2d93 (Base functional for registration)
    print('Start bot(Ctrl-C for stop)')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop bot')
