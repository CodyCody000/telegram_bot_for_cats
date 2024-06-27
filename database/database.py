import aiosqlite
import aiofiles
from enum import StrEnum


class Columns(StrEnum):
    user_id = 'user_id'
    user_is_admin = 'user_is_admin'
    name = 'name'
    username = 'username'
    age = 'age'
    coins = 'coins'


async def init():
    async with (aiosqlite.connect('database.db') as db,
                aiofiles.open(r'./database/init.sql') as file):
        script = await file.read()
        await db.execute(script)
        await db.commit()


async def new_user(user_id, name, username, age):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('REPLACE INTO users(user_id, name, username, age) VALUES (?, ?, ?, ?)',
                         (user_id, name, username, age))
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE user_id = ?',
                              (user_id,)) as cursor:
            return await cursor.fetchone()
