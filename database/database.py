import aiosqlite
import aiofiles
from enum import StrEnum
from database.database_shop import init_shop
from database.database_pool import init_pool

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
    await init_pool()


async def new_user(user_id: int, name: str, username: str | None, age: int) -> None:
    username = username or '-'
    async with aiosqlite.connect('database.db') as db:
        await db.execute('REPLACE INTO users(user_id, name, username, age) VALUES (?, ?, ?, ?)',
                         (user_id, name, username, age))
        await db.commit()


async def get_user(user_id: int) -> aiosqlite.Row | None:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE user_id = ?',
                              (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_users() -> list[aiosqlite.Row]:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users') as cursor:
            return await cursor.fetchall()


async def get_user_username(username: str) -> aiosqlite.Row | None:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE username = ?',
                              (username,)) as cursor:
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
            return row['coins']


async def set_coins_id(coins: int, user_id: int) -> None:
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET coins = ? WHERE user_id = ?',
                         (coins, user_id))
        await db.commit()


async def get_max_coins() -> int:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT MAX(coins) AS max_coins FROM users') as cursor:
            row = await cursor.fetchone()
            return row['max_coins']


async def get_warns(user_id: int) -> int:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT warn_count FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0]


async def incriment_warns(user_id: int) -> None:
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET warn_count = warn_count + 1 WHERE user_id = ?', (user_id,))
        await db.commit()


async def decriment_warns(user_id) -> None:
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET warn_count = warn_count - 1 WHERE user_id = ?', (user_id,))
        await db.commit()


async def clear_warns(user_id: int) -> None:
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET warn_count = 0 WHERE user_id = ?', (user_id,))
        await db.commit()


async def set_ban_state(user_id: int, state: bool):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET is_banned = ? WHERE user_id = ?', (int(state), user_id))
        await db.commit()


async def set_mute_state(user_id: int, state: bool):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE users SET is_muted = ? WHERE user_id = ?', (int(state), user_id))
        await db.commit()
