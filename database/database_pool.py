import aiosqlite
import aiofiles
from time import time

# candidate_id
# user_id
# name
# data
# price
# time_for_candidate
# time_for_poll

# If candidate_id = 1, then user_id - id of creator, name - type of poll, data
# - rules


async def init_pool() -> None:
    async with (aiosqlite.connect('database.db') as db,
                aiofiles.open(r'./database/init_pool.sql') as file):
        script = await file.read()
        await db.execute(script)
        await db.commit()


async def get_contest_info() -> aiosqlite.Row | None:
    async with (aiosqlite.connect('database.db') as db):
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM pool WHERE type_of_row = ?',
                              ('creator',)) as cursor:
            return await cursor.fetchone()


async def get_candidates() -> list[aiosqlite.Row]:
    async with (aiosqlite.connect('database.db') as db):
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM pool WHERE type_of_row = ?',
                              ('candidate',)) as cursor:
            candidates = await cursor.fetchall()
            return list(candidates)


async def get_candidate(name: str) -> aiosqlite.Row:
    async with (aiosqlite.connect('database.db') as db):
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM pool WHERE name = ? AND type_of_row = ?',
                              (name, 'candidate')) as cursor:
            return await cursor.fetchone()


async def incriment_candidate(name: str) -> bool:
    async with (aiosqlite.connect('database.db') as db):
        db.row_factory = aiosqlite.Row
        num_of_votes = 0
        async with db.execute('SELECT num_of_votes FROM pool WHERE name = ?',
                              (name,)) as cursor:
            num_of_votes = await cursor.fetchone()
            if num_of_votes is None:
                return False
            num_of_votes = num_of_votes[0] + 1

        await db.execute('UPDATE pool SET num_of_votes = ? WHERE name = ?',
                         (num_of_votes, name))
        await db.commit()
        return True


async def write_row_in_database(user_id: int, name: str, data: str, price: int,
                                time_for_candidate: int = 24*60*60,
                                time_for_poll: int = 24*60*60,
                                candidate_type='candidate') -> None:
    current_time = time()
    async with (aiosqlite.connect('database.db') as db):
        await db.execute('INSERT INTO pool(type_of_row, user_id, name, data, price, time_for_candidate, time_for_poll) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (candidate_type, user_id, name, data, price, time_for_candidate+current_time, time_for_candidate+time_for_poll+current_time))
        await db.commit()


async def clear_contest() -> None:
    async with (aiosqlite.connect('database.db') as db):
        await db.execute('DELETE FROM pool')
        await db.execute('DELETE FROM sqlite_sequence WHERE name = "pool"')
        await db.commit()
