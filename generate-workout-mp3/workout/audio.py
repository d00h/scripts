from datetime import timedelta
from enum import Enum
from os import makedirs, path
from typing import Iterable

from openai import OpenAI
from pydub import AudioSegment


class AudioVoice(str, Enum):
    """ https://platform.openai.com/docs/guides/text-to-speech """

    alloy = "alloy"
    echo = "echo"
    fable = "fable"
    onyx = "onyx"
    nova = "nova"
    shimmer = "shimmer"


class AudioFactory:

    def __init__(self, voice: AudioVoice, gain_level: int, cache_directory: str):

        self.openai = OpenAI()

        self.voice = voice
        self.gain_level = gain_level
        self.cache_directory = cache_directory

    def say(self, text: str) -> AudioSegment:
        if not path.exists(self.cache_directory):
            makedirs(self.cache_directory)
        cache_filename = path.join(self.cache_directory, text + ".mp3")
        if not path.exists(cache_filename):
            response = self.openai.audio.speech.create(
                model="tts-1",
                voice=self.voice.value,
                input=text
            )
            response.stream_to_file(cache_filename)
        prefix = AudioSegment.silent(duration=100)
        phrase = AudioSegment.from_mp3(cache_filename)
        if self.gain_level:
            phrase = phrase + self.gain_level
        return prefix + phrase

    def silent(self, milliseconds: int) -> AudioSegment:
        return AudioSegment.silent(duration=milliseconds)

    def combine(self, segments: Iterable[AudioSegment]) -> AudioSegment:
        acc = None
        for segment in segments:
            if acc is None:
                acc = segment
            else:
                acc += segment
        return acc or AudioSegment.silent()
