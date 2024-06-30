import asyncio
from dotenv import dotenv_values

from aiogram import Bot, Dispatcher
from app.registration import reg_router, admin_chat_router
from app.coins import group_router, private_router
from app.shop import shop_router, shop_group_router
from database.database import init


async def main():
    bot = Bot(dotenv_values().get('TOKEN'))
    dp = Dispatcher()

    await init()

    dp.include_routers(reg_router, admin_chat_router)
    dp.include_routers(group_router, private_router)
    dp.include_routers(shop_router, shop_group_router)
    print('Start bot(Ctrl-C for stop)')
    await bot.send_message(dotenv_values().get('ADMIN_GROUP_ID'), 'Я запустился^^')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop bot')
