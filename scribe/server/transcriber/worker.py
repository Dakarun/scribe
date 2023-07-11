import whisper

from enum import Enum
from pathlib import Path

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
    def __init__(self, model_size: ModelSize, write_location: Path):
        self.model_size = model_size
        self.write_location = write_location
        self.model = self._load_model()

    def _load_model(self):
        model = whisper.load_model(self.model_size.value)
        return model