from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner
from aiogram.enums import ParseMode
from aiogram import html

from app.filters import IsRegistrated
from database.database import get_coins, set_coins, get_coins_id, set_coins_id  # type: ignore

group_router = Router()
group_router.message.filter(F.chat.type.in_(['group', 'supergroup']),
                            IsRegistrated())


async def is_admin(message: Message):
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))


@group_router.message(Command('give_coins'))
async def give_coins(message: Message, command: CommandObject):
    await message.reply('Принял команду!')
    if not await is_admin(message):
        await message.reply('К сожалению, ты не админ(')
        return

    args = command.args and command.args.split(' ')
    if not (args and (0 < len(args) < 3)) or (len(args) == 1 and not message.reply_to_message):
        await message.reply(f'Непрааавильно ты <s>дядя фёдор</s> {html.quote(message.from_user.first_name)} команду используешь:\n \
либо пишешь <code>/give_coins [количество монеток] @[юзернейм пользователя]</code>, либо ответом на сообщение \
пользователя <code>/give_coins [количество монеток]</code>',
                            ParseMode.HTML)
        return

    try:
        plus_coins = int(args[0])
        if plus_coins <= 0:
            raise ValueError
    except ValueError:
        await message.reply('Ты написал далеко не положительное число(')
        return

    username = args[1][1:] if len(
        args) == 2 else message.reply_to_message.from_user.username

    print(username)

    if username:
        prev_coins = await get_coins(username)
    else:
        prev_coins = await get_coins_id(message.reply_to_message.from_user.id)

    print(prev_coins)

    if prev_coins is None:
        await message.reply('Пользователь не зарегестрирован. Для регистрации зайти в лсочку бота и написать /start ^^')
        return

    if username:
        if username == message.from_user.username:
            await message.reply('Ах ты ж какой хитрец, сам себе отправляет денюшку^^ По попе атата)))')
            return
        await set_coins(prev_coins + plus_coins, username)
    else:
        if message.reply_to_message.from_user.id == message.from_user.id:
            await message.reply('Ах ты ж какой хитрец, сам себе отправляет денюшку^^ По попе атата)))')
            return
        await set_coins_id(prev_coins + plus_coins, message.reply_to_message.from_user.id)

    if username:
        await message.reply(f'Котику @{username} дали {plus_coins} монеток^^')
    else:
        await message.reply(f'Котику {message.reply_to_message.from_user.first_name} дали {plus_coins} монеток^^')


@group_router.message(Command('take_coins'))
async def give_coins(message: Message, command: CommandObject):
    await message.reply('Принял команду!')
    if not await is_admin(message):
        await message.reply('К сожалению, ты не админ(')
        return

    args = command.args and command.args.split(' ')
    if not (args and (0 < len(args) < 3)) or (len(args) == 1 and not message.reply_to_message):
        await message.reply(f'Непрааавильно ты <s>дядя фёдор</s> {html.quote(message.from_user.first_name)} команду используешь:\n \
либо пишешь <code>/take_coins [количество монеток] @[юзернейм пользователя]</code>, либо ответом на сообщение \
пользователя <code>/take_coins [количество монеток]</code>',
                            ParseMode.HTML)
        return

    try:
        minus_coins = int(args[0])
        if minus_coins <= 0:
            raise ValueError
    except ValueError:
        await message.reply('Ты написал далеко не положительное число(')
        return

    username = args[1][1:] if len(
        args) == 2 else message.reply_to_message.from_user.username

    if username:
        prev_coins = await get_coins(username)
    else:
        prev_coins = await get_coins_id(message.reply_to_message.from_user.id)

    if prev_coins < minus_coins:
        minus_coins = prev_coins

    if prev_coins is None:
        await message.reply('Пользователь не зарегестрирован. Для регистрации зайти в лсочку бота и написать /start ^^')
        return

    if username:
        await set_coins(prev_coins - minus_coins, username)
    else:
        await set_coins_id(prev_coins + minus_coins, message.reply_to_message.from_user.id)

    if minus_coins != prev_coins:
        await message.reply(f'У котика {username or message.reply_to_message.from_user.first_name} забрали {minus_coins} монеток((')
    else:
        await message.reply(f'У котика {username or message.reply_to_message.from_user.first_name} забрали все монетки т-т')
