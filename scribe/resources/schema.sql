CREATE TABLE IF NOT EXISTS sessions (
    `session_id` INTEGER PRIMARY KEY,
    `name` TEXT,
    `description` TEXT,
    `start_ts` TEXT,
    `end_ts` TEXT
)
;

CREATE TABLE IF NOT EXISTS transcriptions (
    `transcription_id` INTEGER PRIMARY KEY,
    `session_id` INTEGER,
--     `created` TEXT, TODO: Figure out sqllite triggers to handle timestamp updates
--     `updated` TEXT,
    `storage_backend` TEXT, -- TODO: Figure out sqllite enums
    `location` TEXT
)
