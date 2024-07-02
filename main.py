import asyncio
from aiogram import Bot, Dispatcher
from dotenv import dotenv_values

from app.registration import reg_router, admin_chat_router
from app.coins import group_router
from app.shop import shop_router, shop_group_router
from app.cats_chat import cats_chat
from app.poll import poll_private_router, poll_channel_router

from database.database import init
from aiogram.enums import UpdateType


async def main():
    bot = Bot(dotenv_values().get('TOKEN'))
    dp = Dispatcher()

    await init()

    dp.include_routers(reg_router, admin_chat_router)
    dp.include_routers(group_router)
    dp.include_routers(shop_router, shop_group_router)
    dp.include_routers(cats_chat)
    dp.include_routers(poll_private_router, poll_channel_router)
    print('Start bot(Ctrl-C for stop)')
    await bot.send_message(dotenv_values().get('ADMIN_GROUP_ID'), 'Я запустился^^')
    await dp.start_polling(bot, allowed_updates=[UpdateType.MESSAGE,
                                                 UpdateType.CALLBACK_QUERY,
                                                 UpdateType.CHAT_MEMBER,
                                                 UpdateType.MY_CHAT_MEMBER,
                                                 UpdateType.POLL_ANSWER])

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop bot')
