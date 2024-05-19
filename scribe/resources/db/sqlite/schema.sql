CREATE TABLE IF NOT EXISTS sessions (
    `session_id` INTEGER PRIMARY KEY,
    `created_ts` DATETIME NOT NULL,
    `name` TEXT,
    `description` TEXT,
--     `user_id` INT REFERENCES users.user_id, TODO: Disabled until auth is implemented
    `end_ts` TEXT
)
;

CREATE TABLE IF NOT EXISTS session_entries (
    `session_entry_id` INTEGER PRIMARY KEY,
    `created_ts` DATETIME NOT NULL,
    `session_id` INTEGER REFERENCES sessions.session_id,
--     `user_id` INT REFERENCES users.user_id, TODO: Disabled until auth is implemented
    `file` TEXT
)
;

CREATE TABLE IF NOT EXISTS transcriptions (
    `transcription_id` INTEGER PRIMARY KEY,
    `created_ts` DATETIME NOT NULL, -- TODO: Figure out sqllite triggers to handle timestamp updates
    `updated_ts` DATETIME,
    `session_id` INTEGER REFERENCES sessions.session_id,
    `storage_backend` TEXT, -- TODO: Figure out sqllite enums
    `base_location` TEXT,
    `default_transcription` BOOLEAN
)
;

CREATE TABLE IF NOT EXISTS transcription_entries (
    `transcription_entry_id` INTEGER PRIMARY KEY,
    `created_ts` DATETIME NOT NULL,
    `updated_ts` DATETIME,
--     `user_id` INT REFERENCES users.user_id, TODO: Disabled until auth is implemented
    `session_entry_id` INTEGER REFERENCES session_entries.session_entry_id,
    `transcription_id` INTEGER REFERENCES transcriptions.trancription_id,
    `location` TEXT,
    `is_active` BOOLEAN
)
;
