CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role INTEGER
);

CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    name TEXT,
    user_id INTEGER REFERENCES users,
    visible BOOLEAN
);

CREATE TABLE chains (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas,
    subject TEXT,
    first_message TEXT,
    user_id INTEGER REFERENCES users,
    visible BOOLEAN
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    user_id INTEGER REFERENCES users,
    sent_at TIMESTAMP,
    chain_id INTEGER REFERENCES chains,
    visible BOOLEAN
);

CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    liketype VARCHAR(10),
    user_id INTEGER REFERENCES users,
    message_id integer REFERENCES messages,
    CONSTRAINT unique_like_dislike UNIQUE (user_id, message_id)
);