import aiosqlite
import aiofiles

# product_id
# title
# description
# author_id
# price


async def init_shop() -> None:
    async with (aiosqlite.connect('database.db') as db,
                aiofiles.open(r'./database/init_shop.sql') as file):
        script = await file.read()
        await db.execute(script)
        await db.commit()


async def add_product(title: str, description: str, author_id: int, price: int) -> None:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        await db.execute('INSERT INTO shop(title, description, author_id, price) VALUES (?, ?, ?, ?)',
                         (title, description, author_id, price))
        await db.commit()


async def get_list_of_products(author_id: int | None = None) -> int:
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        rows = []
        if author_id is None:
            async with db.execute('SELECT title, product_id FROM shop') as cursor:
                async for row in cursor:
                    rows.append((row['title'], row['product_id']))
        else:
            async with db.execute('SELECT title, product_id FROM shop WHERE author_id = ?',
                                  (author_id,)) as cursor:
                async for row in cursor:
                    rows.append((row['title'], row['product_id']))
        return rows or None


async def get_product(product_id: int) -> aiosqlite.Row:
    async with aiosqlite.connect('database.db') as db:
        async with db.execute('SELECT * FROM shop WHERE product_id = ?',
                              (product_id,)) as cursor:
            return await cursor.fetchone()


async def remove_product(product_id: int):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('DELETE FROM shop WHERE product_id = ?', (product_id,))
        await db.commit()
