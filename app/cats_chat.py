from aiogram import Router, F, html
from aiogram.types import Message, ChatMemberUpdated
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner
from aiogram.filters import ChatMemberUpdatedFilter, Command
from aiogram.filters.chat_member_updated import JOIN_TRANSITION, IS_ADMIN
from aiogram.enums import ParseMode
from dotenv import dotenv_values

from database.database import get_user, get_user_username
from app.filters import IsRegistrated, IsNotMuted, IsInChatAndChannel

cats_chat = Router()
cats_chat.message.filter(F.chat.type.in_(['group', 'supergroup']),
                         IsRegistrated(), IsNotMuted(), IsInChatAndChannel())
actions = {
    'обнять': ('{} обнял котика {} 🤗', 'HUGGING'),
    'шлёпнуть': ('{} шлёпнул котика {} 👋', 'SLAPPING'),
    'поцеловать': ('{} поцеловал котика {} 💋', 'KISSING'),
    'постонать': ('{} постонал котику {} 🥵', 'MOANING'),
    'отсосать': ('{} отсосал котику {} 👅', 'SUCKING'),
    'выебать': ('{} выебал котика {} 🍆', 'FUCKING'),
    'кончить': ('{} кончил на/в котика {} 💦', 'CUMMING'),
    'погладить': ('{} погладил котика {} 😊', 'STROKING'),
    'прижать': ('{} прижал котика {} 😳', 'PINNING')
}


@cats_chat.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def added_to_group(event: ChatMemberUpdated):
    if isinstance(event.new_chat_member, (ChatMemberAdministrator, ChatMemberOwner)):
        await event.answer('Привет, спасибо, что добавили меня в этот прекрасный чат, как админчика^^')
    else:
        await event.answer('Привет, спасибо, что добавили меня в этот прекрасный чат^^ \
Сделайте меня админчиком, чтобы я работал👉👈')

    await event.bot.send_message(dotenv_values().get('CREATOR_ID'),
                                 f'ID-чатика: {event.chat.id}')


@cats_chat.my_chat_member(ChatMemberUpdatedFilter(IS_ADMIN))
async def added_to_admins(event: ChatMemberUpdated):
    await event.answer('Cпасибо, что сделали меня админчиком^^')


@cats_chat.message(Command('list_of_actions'))
async def list_of_actions(message: Message):
    message_reply = f'Списочек действий^^:\n\n• {'\n\n• '.join(html.code(a.capitalize()) for a in actions)}\n\n\
Чтобы применить действие, нужно написать {html.code('[действие] @[юзернейм]')} или просто {html.code('[действие]')} ответом на сообщение^^'
    await message.reply(message_reply, parse_mode=ParseMode.HTML)


# Оставляй в самом низу
@cats_chat.message(F.reply_to_message)
@cats_chat.message(F.text)
async def action(message: Message):
    command, *username = message.text.split()

    if (command := command.lower()) not in actions:
        return

    action = actions[command]

    from_user_data = await get_user(message.from_user.id)
    from_user_link = html.link(
        from_user_data['name'], f'tg://user?id={message.from_user.id}')

    if message.reply_to_message:
        to_user_data = await get_user(message.reply_to_message.from_user.id)
    else:
        to_user_data = await get_user_username(username[0].removeprefix('@'))

    if to_user_data is None:
        if message.reply_to_message.from_user.is_bot:
            to_user_link = html.link(
                message.reply_to_message.from_user.full_name,
                f'tg://user?id={message.reply_to_message.from_user.id}')
        else:
            return
    else:
        to_user_link = html.link(
            to_user_data['name'], f'tg://user?id={to_user_data['user_id']}')

    message_text = action[0].format(from_user_link, to_user_link)

    if not message.reply_to_message and username[1:]:
        message_text += f', cо словами: {' '.join(username[1:])}'
    elif message.reply_to_message and username:
        message_text += f', cо словами: {' '.join(username)}'

    await message.reply_document(dotenv_values(f'./app/.mediaenv').get(action[1]),
                                 caption=message_text,
                                 parse_mode=ParseMode.HTML)
