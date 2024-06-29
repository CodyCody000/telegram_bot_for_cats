CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    user_is_admin INTEGER NOT NULL DEFAULT 0,
    name TEXT UNIQUE NOT NULL CHECK (name != ''),
    username TEXT NOT NULL CHECK (username != ''),
    age INTEGER NOT NULL CHECK (age BETWEEN 0 AND 17),
    coins INTEGER NOT NULL DEFAULT 0
)