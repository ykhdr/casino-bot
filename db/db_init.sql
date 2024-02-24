CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username varchar,
  balance BIGINT,
  chat_id INTEGER REFERENCES chats(id)
);