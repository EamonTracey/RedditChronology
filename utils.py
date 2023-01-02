import random
import re
import typing

import ffmpeg
from google.cloud import texttospeech


def media_duration(file: str):
    probe = ffmpeg.probe(file)
    return float(probe["format"]["duration"])


def chunk(collection: typing.Collection, size: int):
    i = 0
    while i < len(collection):
        yield collection[i:i + size]
        i += size


def format_score(score: int) -> str:
    if score < 1000:
        return str(score)
    scstr = str(score // 100)
    return scstr[:-1] + "." + scstr[-1] + "K"


def random_voice_params() -> texttospeech.VoiceSelectionParams:
    return texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-" + random.choice("ABCDEFGHIJ")
    )


def text_cuts(text) -> list[str]:
    # These characters will be used as delimiters
    # for naturally cutting comment text.
    cut_delimiters = ".,:?!"

    # This pattern effectively allows us to
    # split a string by repeating delimiters.
    cut_pattern = re.compile(rf"[^{cut_delimiters}]*[{cut_delimiters}]*")

    # Cut the text using our regex pattern from above.
    matches = cut_pattern.findall(text)
    matches = list(filter(None, matches))

    return matches
