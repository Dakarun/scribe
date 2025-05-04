import logging

from dataclasses import dataclass
from scribe.server.models import SessionEntry, TranscriptionEntry
from pathlib import Path
from werkzeug.datastructures.file_storage import FileStorage


@dataclass
class FileManager:
    location: str

    def __post_init__(self):
        self.logger = self._logger()

    def save(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def _logger(self) -> logging.Logger:
        log_format = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
        logging.basicConfig(format=log_format)
        logger = logging.getLogger(self.__name__)
        return logger

    def create_parent_dir(self) -> None:
        parent_dir = Path(self.location).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)


@dataclass
class SessionEntryFileManager(FileManager):
    session_entry: SessionEntry
    payload: FileStorage

    def save(self):
        self.logger.info(f"Received SessionEntry file {self.payload}, writing to {self.location}")
        self.create_parent_dir()
        self.payload.save(self.location)


@dataclass
class TranscriptionEntryFileManager(FileManager):
    transcription_entry: TranscriptionEntry
    payload: str

    def save(self):
        self.create_parent_dir()
        with open(self.location, "w+") as f:
            f.write(self.payload)
