CREATE TABLE IF NOT EXISTS shop (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (name != ''),
    description TEXT NOT NULL CHECK (name != ''),
    author_id INTEGER NOT NULL,
    price INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE
)