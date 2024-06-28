import aiosqlite
import aiofiles
from enum import StrEnum
from database.database_shop import init_shop

# user_id
# user_is_admin
# name
# username
# age
# coins


async def init() -> None:
    async with (aiosqlite.connect('database.db') as db,
                aiofiles.open(r'./database/init.sql') as file):
        script = await file.read()
        await db.execute(script)
        await db.commit()
        await init_shop()


async def new_user(user_id: int, name: str, username: str | None, age: int) -> None:
    username = username or '-'
    async with aiosqlite.connect('database.db') as db:
        await db.execute('REPLACE INTO users(user_id, name, username, age) VALUES (?, ?, ?, ?)',
                         (user_id, name, username, age))
        await db.commit()


async def get_user(user_id: int) -> aiosqlite.Row:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE user_id = ?',
                              (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_coins(username: str) -> int:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT coins FROM users WHERE username = ?',
                              (username,)) as cursor:
            row = await cursor.fetchone()
            return row and row['coins']


async def set_coins(coins: int, username: str) -> None:
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET coins = ? WHERE username = ?',
                         (coins, username))
        await db.commit()


async def get_coins_id(user_id: int) -> int:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT coins FROM users WHERE user_id = ?',
                              (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row and row['coins']


async def set_coins_id(coins: int, user_id: int) -> None:
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET coins = ? WHERE user_id = ?',
                         (coins, user_id))
        await db.commit()
