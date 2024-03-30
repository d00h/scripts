import logging
from argparse import ArgumentParser
from datetime import timedelta
from os import getcwd, path

from .audio import AudioFactory, AudioVoice
from .output import OutputBuilder, OutputFormat

log = logging.getLogger(__name__)


def init_logger():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s : %(message)s")
    )

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()

    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output-directory",
        default=path.join(getcwd(), "output"),
    )
    output_group.add_argument(
        "--output-format",
        type=OutputFormat, choices=OutputFormat, default=OutputFormat.combine
    )

    audio_group = parser.add_argument_group("Audio")
    audio_group.add_argument(
        "--voice", type=AudioVoice, choices=AudioVoice, default=AudioVoice.nova
    )
    audio_group.add_argument("--gain-level", type=int,  default=0)
    audio_group.add_argument("--cache-directory", default=path.join(getcwd(), "cache"))
    audio_group.add_argument("--bit-rate", default="192k")

    parser.add_argument("command", choices=["generate"])

    return parser


class Workout:

    @classmethod
    def from_cmdline(cls, name: str) -> "Workout":
        parser = create_parser()
        args = parser.parse_args()

        init_logger()

        output_factory = OutputBuilder.get_factory(args.output_format)
        output_builder = output_factory(
            output_directory=args.output_directory,
            workout_name=name,
            bit_rate=args.bit_rate
        )

        audio_factory = AudioFactory(
            voice=args.voice,
            gain_level=args.gain_level,
            cache_directory=args.cache_directory,
        )
        return cls(
            audio_factory=audio_factory,
            output_builder=output_builder,
        )

    def __init__(self, audio_factory: AudioFactory, output_builder: OutputBuilder):
        self.audio_factory = audio_factory
        self.output_builder = output_builder
        self.acc_word, self.acc_audio = [], []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.output_builder.close()

    def say(self, *text) -> "Workout":
        if self.acc_word:
            self.flush()
        for word in text:
            audio = self.audio_factory.say(word)
            self.acc_word.append(word)
            self.acc_audio.append(audio)
        return self

    def wait(
        self, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0
    ) -> "Workout":
        total_milliseconds = ((minutes + hours * 60) * 60 + seconds) * 1000 + milliseconds
        audio = self.audio_factory.silent(total_milliseconds)
        self.acc_audio.append(audio)
        return self

    def flush(self):
        if not self.acc_word:
            return
        name = " ".join(self.acc_word)
        log.info(f"step {name}")
        audio = self.audio_factory.combine(self.acc_audio)
        self.output_builder.append(name, audio)

        self.acc_word, self.acc_audio = [], []
