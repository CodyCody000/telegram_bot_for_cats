from aiogram import F, Router, html
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from app.registration import generate_invite_link
from dotenv import dotenv_values

from aiosqlite import Row
from asyncio import sleep

from app.filters import (IsInChatAndChannel, CorrectCommand, IsNotMuted,
                         IsRegistrated, IsNotBanned)
from database.database import (get_user_username, set_ban_state, set_mute_state,
                               incriment_warns, decriment_warns, get_users)
from database.database import clear_warns as _clear_warns

group_commands_router = Router()
group_commands_router.message.filter(F.chat.type.in_(['group', 'supergroup']),
                                     IsRegistrated(), IsNotMuted(), IsInChatAndChannel())
mailing_router = Router()
mailing_router.message.filter(F.chat.type == 'private', IsRegistrated(),
                              IsNotBanned(), IsInChatAndChannel())


async def is_admin(message: Message):
    member = await message.bot.get_chat_member(dotenv_values()['CATS_GROUP_ID'], message.from_user.id)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))


async def user_getter(message: Message, command: CommandObject):
    if message.reply_to_message:
        username = message.reply_to_message.from_user.username
    else:
        username = command.args.removeprefix('@')

    return await get_user_username(username)


@group_commands_router.message(Command('ban'), CorrectCommand())
async def ban(message: Message, command: CommandObject,
              user_info: Row | None = None):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    if user_info is None:
        user_info = await user_getter(message, command)
        if not user_info:
            await message.reply(f'Пользователь не зарегестрирован, для регистрации надо написать ботику в лс {html.code('/start')}',
                                parse_mode=ParseMode.HTML)
            return

    await message.chat.ban(user_info['user_id'])
    await set_ban_state(user_info['user_id'], True)
    await message.answer(f'Котя @{user_info['username']} к сожаленьицу забанен, помянем 😔')


@group_commands_router.message(Command('unban'), CorrectCommand())
async def unban(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    user_info = await user_getter(message, command)
    if not user_info:
        await message.reply(f'Пользователь не зарегестрирован, для регистрации надо написать ботику в лс {html.code('/start')}',
                            parse_mode=ParseMode.HTML)
        return

    await message.chat.unban(user_info['user_id'])
    await set_ban_state(user_info['user_id'], False)
    await _clear_warns(user_info['user_id'])
    invite_link = await generate_invite_link(message.bot)
    await message.bot.send_message(user_info['user_id'],
                                   f'Мы приглашает тебя обратьно, вот ссылочка {invite_link} ^^')
    await message.answer(f'Котю @{user_info['username']} к счастью разбанили, уря^^ А ещё он был приглашён обратненько')


@group_commands_router.message(Command('mute'), CorrectCommand())
async def mute(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    user_info = await user_getter(message, command)
    if not user_info:
        await message.reply(f'Пользователь не зарегестрирован, для регистрации надо написать ботику в лс {html.code('/start')}',
                            parse_mode=ParseMode.HTML)
        return

    await set_mute_state(user_info['user_id'], True)
    await message.answer(f'Для коти @{user_info['username']} установлена молчанка!')


@group_commands_router.message(Command('unmute'), CorrectCommand())
async def unmute(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    user_info = await user_getter(message, command)
    if not user_info:
        await message.reply(f'Пользователь не зарегестрирован, для регистрации надо написать ботику в лс {html.code('/start')}',
                            parse_mode=ParseMode.HTML)
        return

    await set_mute_state(user_info['user_id'], False)
    await message.answer(f'@{user_info['username']}, молчанка закончена^^')


@group_commands_router.message(Command('kick'), CorrectCommand())
async def kick(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    user_info = await user_getter(message, command)
    if not user_info:
        await message.reply(f'Пользователь не зарегестрирован, для регистрации надо написать ботику в лс {html.code('/start')}',
                            parse_mode=ParseMode.HTML)
        return

    await message.chat.ban(user_info['user_id'])
    await message.chat.unban(user_info['user_id'])
    await message.answer(f'Котика @{user_info['username']} кикнули, грусьня(')


@group_commands_router.message(Command('warn'))
async def warn(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    user_info = await user_getter(message, command)
    if not user_info:
        await message.reply(f'Пользователь не зарегестрирован, для регистрации надо написать ботику в лс {html.code('/start')}',
                            parse_mode=ParseMode.HTML)
        return

    await incriment_warns(user_info['user_id'])
    current_warns = user_info['warn_count'] + 1
    if current_warns >= 3:
        await ban(message, command, user_info)
        return
    await message.answer(f'Котика @{user_info["username"]} предупредили, у него уже {current_warns} варна из 3. Надеюсь больше он не будет баловаться^^')
    await message.answer('Через недельку этот варник уберётся^^')
    await sleep(7*24*60*60)
    await decriment_warns(user_info['user_id'])


@group_commands_router.message(Command('clear_warns'), CorrectCommand())
async def clear_warns(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    user_info = await user_getter(message, command)
    if not user_info:
        await message.reply(f'Пользователь не зарегестрирован, для регистрации надо написать ботику в лс {html.code('/start')}',
                            parse_mode=ParseMode.HTML)
        return

    await _clear_warns(user_info['user_id'])
    await message.answer(f'У котика @{user_info["username"]} все варны были стёрты, крутяк^^')


@group_commands_router.message(Command('call'))
async def call(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    if command.args:
        message_text = f'Созывает котят со словами: "{command.args}"\n'
    else:
        message_text = 'Созывает котят\n'

    for user in await get_users():
        message_text += f'\n• {html.link(user['name'],
                                         f'tg://user?id={user["user_id"]}')}'

    await message.reply(message_text,
                        parse_mode=ParseMode.HTML)


@mailing_router.message(Command('call'))
async def call_mailing(message: Message, command: CommandObject):
    if not await is_admin(message):
        await message.answer('Ты не админчик((')
        return

    if command.args:
        message_text = f'Тут рассылочка произошла с таким текстом: {
            command.args}'
    else:
        message_text = 'Тут рассылочка произошла, посмотри, мб в чатике что нить'

    for user in await get_users():
        await message.bot.send_message(user['user_id'], message_text)
