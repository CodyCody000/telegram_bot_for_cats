CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
    user_is_admin INTEGER NOT NULL CHECK (user_is_admin IN [0, 1]) DEFAULT 0
    name TEXT UNIQUE NOT NULL CHECK (name != '')
    username TEXT UNIQUE NOT NULL CHECK (name != '')
    age INTEGER NOT NULL CHECK (age BETWEEN 0 AND 17)
    coins INTEGER NOT NULL DEFAULT 0
)