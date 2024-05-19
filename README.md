# scribe

# Requirements
## System packages
```
sudo apt install portaudio19-dev ffmpeg
```

# Installation
```
git clone
poetry shell
poetry install
```

Init DB
```
flask --app scribe.server init-db
```

# Backend Design
Features
- Multiple users can contribute to the same transcription
- Transcriptions can be replayed

## Entities
- User
- Session
- Session Entry
- Transcription
- Transcription Entry

```mermaid
---
title: Order example
---
erDiagram
    user ||--|{ session : "is owner of"
    user ||--|{ session_entry : uploaded
    user ||--|{ transcription_entry : "is speaker of"
    
    session ||--|{ session_entry : "Is container for"
    session ||--|{ transcription : "Is parent of"
    
    session_entry ||--|{ transcription_entry : "Is source of"
    
    transcription ||--|{ transcription_entry : "Is container of"
    
    user {
        long user_id PK "monotonic id"
        string source "Where the user is sourced from"
        string name "Display name"
        string email "Email address (Might not be needed)"
    }
    
    session {
        long session_id PK "monotonic id"
        string description
        long user_id FK "Owner of the session"
        timestamp created_ts "When did the session start"
        timestamp end_ts "When was the session closed"
    }
    
    session_entry {
        long session_entry_id PK
        timestamp created_ts
        long session_id FK "FK to session"
        long user_id FK "Submitter of entry"
        string file "Path to file submitted"
    }
    
    transcription {
        long transcription_id PK
        timestamp created_ts
        timestamp updated_ts
        long session_id FK "FK to session"
        string storage_backend "Backend for file transcriptions (local, s3 etc)"
        string base_location "Parent location for files belonging to transcription"
        bool default_transcription "Is this the default transcription"
    }
    
    transcription_entry {
        long transcription_entry_id PK
        timestamp created_ts "Time record was created"
        timestamp updated_ts "Time record was updated, might not be necessary if entity is immutable"
        long user_id FK "Speaker of entry"
        long session_entry_id FK "Session entry the transcription is sourced from"
        long transcription_id FK "Belongs to transcription"
        string location "Transcription location (assumes it's written to disk/object store)"
        bool is_active "Is this actively used in the transcription"
    }
```

### User
Represents a users, pretty straight forward.

| What    | Description                         |
|---------|-------------------------------------|
| user_id | monotonic id                        |
| source  | Where the user is sourced from      |
| name    | Display name                        |
| email   | Email address (might not be needed) |


### Session
A session in which users have submitted audio for transcription. Main entity for managing transcriptions.

| What        | Description          |
|-------------|----------------------|
| session_id  | monotonic id         |
| description |                      |
| user_id     | Owner of the session |
| start_ts    |                      |
| end_ts      |                      |

### Session Entry
Represents a file submitted to a session. User and timestamps are used display when what parts were spoken.

| What             | Description              |
|------------------|--------------------------|
| session_entry_id | monotonic id             |
| created_ts       | Time record was inserted |
| session_id       | FK to session            |
| user_id          | Submitter of entry, FK   |
| file             | Path to file submitted   |


### Transcription
A transcription. Doesn't contain text, but is more a container. This is done so we can track timestamps and speakers on 
individual transcriptions. Due to the non-deterministic nature of ML, as well as the different accuracies between models
depending on size and languages trained on, we should be able to support rerunning transcriptions on the entire dataset,
or individual entries (see below). Therefor there can be multiple transcriptions per session.

| What                  | Description                                          |
|-----------------------|------------------------------------------------------|
| transcription_id      | monotonic id                                         |
| created_ts            | Time record was inserted                             |
| updated_ts            | Time record was updated                              |
| session_id            | FK to session                                        |
| storage_backend       | Backend for transcription files (local, s3 etc)      |
| base_location         | Parent location for files belonging to transcription |
| default_transcription | Is this the default transcription                    |

### Transcription Entry
An actual transcription of a file. One or more entries make up an actual transcription. TODO: Decide on whether the
transcription should be stored on the db, or on disk/object store.

| What                   | Description                                     |
|------------------------|-------------------------------------------------|
| transcription_entry_id | monotonic id                                    |
| created_ts             | Time record was inserted                        |
| updated_ts             | Time record was updated                         |
| user_id                | Speaker of entry, user FK                       |
| session_entry_id       | Session entry the transcription is sourced from |
| transcription_id       | Belongs to transcription, FK                    |
| location               | Transcription location                          |
| is_active              | Is this actively used in a transcription        |


## User actions
The user can 
- Start/end a session
- Read a transcription
- Submit a session for reprocessing
- Submit a transcription_entry for reprocessing

A user can potentially:
- Reorder transcription entries
- Split transcription entries


### Start/end session
All these graphs assume the user is logged in

```mermaid
flowchart TB
    user((User))
    index[ /index]
    
    active_session{Is the user\nparticipating\nin a session?}
    session_owner{Is the user\nthe owner?}
    
    default[Default page]
    active_session_page[Render active session page]
    end_session_button[Render end session button]
    
    user -- Visits --> index
    index --> active_session
    active_session -- No ----> default
    active_session -- Yes --> active_session_page
    
    active_session_page --> session_owner
    session_owner -- Yes --> end_session_button
    session_owner -- No --> Nothing 
```

### Read a transcription
```mermaid
flowchart TB
    user((User))
    index[ /index]
    select_session[User selects past session]
    sessions[ /sessions?session_id=...]
    default_transcription[Read default transcription]
    multiple_transcriptions{Multiple\nTranscriptions?}
    render_additional_transcriptions[Render additional transcriptionps]
    select_alternative_transcription[User selects non-default transcription]
    transcriptions[ /transcriptions?transcription_id=...]
    
    user -- Visits --> index 
    index --> select_session
    select_session --> sessions
    sessions --> default_transcription
    sessions --> multiple_transcriptions
    multiple_transcriptions -- Yes --> render_additional_transcriptions
    render_additional_transcriptions --> select_alternative_transcription
    select_alternative_transcription --> transcriptions
```

### Submit a session for reprocessing
```mermaid
flowchart TB
    user((User))
    sessions[ /sessions?session_id=...]
    reprocess[User invokes reprocessing]
    transcription[(scribe.transcription)]
    session_entry[(scribe.session_entry)]
    transcription_entry[(scribe.transcription_entry)]
    reprocessing_action[Reprocessing]
    
    user -- Visits --> sessions
    sessions --> reprocess
    
    subgraph reprocessing
        direction TB
        reprocessing_action -- Inserts record into --> transcription
        reprocessing_action -- Selects all entries for selected session --> session_entry
        reprocessing_action -- Inserts new transcription entries for new transcription into --> transcription_entry
        transcription_entry & reprocessing_action -- Marks new transcription as active\n old as inactive --> transcription
    end
    
    reprocess --> reprocessing
```