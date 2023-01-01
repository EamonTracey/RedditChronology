import typing

import ffmpeg


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
