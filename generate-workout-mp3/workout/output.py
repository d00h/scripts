import logging
from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from os import makedirs, path
from typing import Type

from pydub import AudioSegment

log = logging.getLogger(__name__)


class OutputFormat(Enum):

    dry = "dry"
    combine = "combine"
    split = "split"


def format_timedelta(segment: AudioSegment) -> str:
    total = timedelta(milliseconds=int(len(segment)))
    return "".join(
        f"{value}{dim}" for dim, value in {
            "d": total.days,
            "h": total.seconds//3600,
            "m": (total.seconds//60) % 60,
            "s": (total.seconds % 60),
        }.items() if value
    )


class OutputBuilder(ABC):

    @staticmethod
    def get_factory(output_format: OutputFormat) -> Type["OutputBuilder"]:
        match output_format:
            case OutputFormat.dry:
                return DryOutputBuilder
            case OutputFormat.combine:
                return CombineOutputBuilder
            case OutputFormat.split:
                return SplitOutputBuilder
        raise ValueError(output_format)

    def __init__(self, output_directory: str, workout_name: str, bit_rate: str):
        self.output_directory = output_directory
        self.workout_name = workout_name
        self.bit_rate = bit_rate

    @abstractmethod
    def append(self, step_name: str, segment: AudioSegment):
        pass

    @abstractmethod
    def close(self):
        pass


class DryOutputBuilder(OutputBuilder):

    def append(self, step_name: str, segment: AudioSegment):
        pass

    def close(self):
        pass


class SplitOutputBuilder(OutputBuilder):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.idx = 0

    def append(self, step_name: str, segment: AudioSegment):
        output_directory = path.join(self.output_directory, self.workout_name)
        if not path.exists(output_directory):
            makedirs(output_directory)

        self.idx += 1
        total = format_timedelta(segment)
        filename = path.join(output_directory, f"{self.idx} - {step_name} - {total}.mp3")
        log.info(f"save {filename}")
        segment.export(filename, format="mp3", bitrate=self.bit_rate)

    def close(self):
        pass


class CombineOutputBuilder(OutputBuilder):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.acc = AudioSegment.silent()

    def append(self, step_name: str, segment: AudioSegment):
        self.acc = self.acc + segment

    def close(self):
        if not path.exists(self.output_directory):
            makedirs(self.output_directory)

        total = format_timedelta(self.acc)
        filename = path.join(self.output_directory, f"{self.workout_name}-{total}.mp3")
        log.info(f"save {filename}")
        self.acc.export(filename, format="mp3", bitrate=self.bit_rate)
