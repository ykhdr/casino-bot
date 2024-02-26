CREATE TABLE IF NOT EXISTS chats (
    id BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY,
  username varchar,
  balance BIGINT,
  chat_id BIGINT REFERENCES chats(id)
);