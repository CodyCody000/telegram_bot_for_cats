CREATE TABLE IF NOT EXISTS pool (
    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type_of_row TEXT NOT NULL CHECK (name != ''),
    name TEXT UNIQUE NOT NULL CHECK (name != ''),
    data TEXT UNIQUE NOT NULL,
    time_for_candidate INTEGER NOT NULL DEFAULT 86400,
    time_for_poll INTEGER NOT NULL DEFAULT 86400,
    price INTEGER NOT NULL DEFAULT 0,
    num_of_votes INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)