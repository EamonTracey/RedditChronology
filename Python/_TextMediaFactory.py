import abc
import random
import re

import html2image
from google.cloud import texttospeech


class _TextMediaFactory(abc.ABC):
    # These characters will be used as delimiters
    # for naturally cutting comment text.
    cut_delimiters = ".,:?!"

    # This pattern effectively allows us to
    # split a string by repeating delimiters.
    cut_pattern = re.compile(rf"[^{cut_delimiters}]*[{cut_delimiters}]*")

    hti = html2image.Html2Image()

    def __init__(self, text: str, pdir: str, voice_params: texttospeech.VoiceSelectionParams = None):
        self.text = text
        self.pdir = pdir

        if voice_params is None:
            voice_params = self._random_voice_params()
        self.voice_params = voice_params

        # When manufacturing images and audio, we want
        # to cut the comment into natural fragments.
        # These natural fragments are delimited by
        # punctuation including periods, ellipses, commas,
        # colons, question marks, and exclamation points.
        self.text_cuts = self._load_text_cuts()

    def _load_text_cuts(self) -> list[str]:
        # Cut the text using our regex pattern from above.
        matches = self.cut_pattern.findall(self.text)
        matches = list(filter(None, matches))

        return matches

    @staticmethod
    def _random_voice_params() -> texttospeech.VoiceSelectionParams:
        return texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-" + random.choice("ABCDEFGHIJ")
        )

    @abc.abstractmethod
    def manufacture_images(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def manufacture_audios(self) -> list[str]:
        raise NotImplementedError
