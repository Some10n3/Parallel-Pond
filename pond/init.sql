CREATE TABLE IF NOT EXISTS fish (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    position_x INT NOT NULL,
    position_y INT NOT NULL,
    remaining_lifetime FLOAT NOT NULL,
    frames JSONB NOT NULL
);
