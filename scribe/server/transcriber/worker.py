import logging
import whisper

from enum import Enum
from logging import Logger
from pathlib import Path
from queue import Queue
from whisper import Whisper


class ModelSize(Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

    TINY_EN = "tiny.en"
    BASE_EN = "base.en"
    SMALL_EN = "small.en"
    MEDIUM_EN = "medium.en"
    LARGE_EN = "large.en"


class TranscriberWorker:
    def __init__(self, model_size: ModelSize, session_filename: str, write_location: str):
        self.model_size = model_size
        self.session_filename = session_filename
        self.write_location = write_location
        self.queue = Queue()
        self.model = self._load_model()
        self.log = self._get_logger()

    def _load_model(self) -> Whisper:
        model = whisper.load_model(self.model_size.value)
        return model

    def _get_logger(self) -> Logger:
        logging.basicConfig(filename="transcriber_worker.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        logger = logging.getLogger(self.__class__.__name__)
        return logger

    def _write_to_staging_file(self, text: str) -> None:
        staging_file = Path(f"/tmp/scribe/staging/{self.session_filename}")
        with open(staging_file, "a+") as f:
            f.write(text)

    def _commit_file_to_backend(self) -> None:
        pass

    def _archive_data(self) -> None:
        pass

    def put_on_queue(self, audio: bytes) -> None:
        self.queue.put(audio)

    def transcribe(self, audio_file_location) -> None:
        transcription = self.model.transcribe(audio_file_location)
        self._write_to_staging_file(transcription["text"].strip())

    def end_session(self):
        self._commit_file_to_backend()
