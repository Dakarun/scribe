from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean
from scribe.server.db import Base


class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(BigInteger, primary_key=True)
    created_ts = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    # user_id = Column(BigInteger, nullable=False)
    end_ts = Column(DateTime)

    def __init__(self, session_id: int = None, created_ts: datetime = None, name: str = None, description: str = None, end_ts: datetime = None):
        self.session_id = session_id
        self.created_ts = created_ts
        self.name = name
        self.description = description
        self.end_ts = end_ts

    def __repr__(self):
        # TODO: Implement entity representation
        pass


class SessionEntry(Base):
    __tablename__ = "session_entries"
    session_entry_id = Column(BigInteger, primary_key=True)
    created_ts = Column(DateTime, nullable=False)
    session_id = Column(BigInteger, nullable=False)
    # user_id = Column(BigInteger, nullable=False)
    file = Column(String, nullable=False)

    def __init__(self, session_entry_id: int = None, created_ts: datetime = None, session_id: int = None, file: str = None):
        self.session_entry_id = session_entry_id
        self.created_ts = created_ts
        self.session_id = session_id
        self.file = file

    def __repr__(self):
        # TODO: Implement entity representation
        pass


class Transcription(Base):
    __tablename__ = "transcription"
    transcription_id = Column(BigInteger, primary_key=True)
    created_ts = Column(DateTime, nullable=False)
    updated_ts = Column(DateTime)
    session_id = Column(BigInteger, nullable=False)
    storage_backend = Column(String, nullable=False)
    base_location = Column(String, nullable=False)
    default_transcription = Column(Boolean, nullable=False)

    def __init__(self, transcription_id: int = None, created_ts: datetime = None, updated_ts: datetime = None, session_id: int = None, storage_backend: str = None, base_location: str = None, default_transcription: bool = None):
        self.transcription_id = transcription_id
        self.created_ts = created_ts
        self.updated_ts = updated_ts
        self.session_id = session_id
        self.storage_backend = storage_backend
        self.base_location = base_location
        self.default_transcription = default_transcription

    def __repr__(self):
        # TODO: Implement entity representation
        pass


class TranscriptionEntry(Base):
    __tablename__ = "transcription_entries"
    transcription_entry_id = Column(BigInteger, primary_key=True)
    created_ts = Column(DateTime, nullable=False)
    updated_ts = Column(DateTime)
    # user_id = Column(BigInteger, nullable=False)
    session_entry_id = Column(BigInteger, nullable=False)
    transcription_id = Column(BigInteger, nullable=False)
    location = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)

    def __init__(self, transcription_entry_id: int = None, created_ts: datetime = None, updated_ts: datetime = None, session_entry_id: int = None, transcription_id: int = None, location: str = None, is_active: bool = None):
        self.transcription_entry_id = transcription_entry_id
        self.created_ts = created_ts
        self.updated_ts = updated_ts
        # self.user_id = user_id
        self.session_entry_id = session_entry_id
        self.transcription_id = transcription_id
        self.location = location
        self.is_active = is_active

    def __repr__(self):
        # TODO: Implement entity representation
        pass
