import html
import itertools
import os

import praw.models
from PIL import Image
from google.cloud import texttospeech

from html_formats import title_html_format
from _HTIMediaFactory import _HTIMediaFactory
import utils


class _RedditTitleMediaFactory(_HTIMediaFactory):
    def __init__(self, submission: praw.models.Submission):
        self.submission = submission
        self._text_cuts = utils.text_cuts(self.submission.title)

        super(_RedditTitleMediaFactory, self).__init__()

    def manufacture_images(self) -> list[str]:
        image_files = []

        for i, cut in enumerate(itertools.accumulate(self._text_cuts)):
            # Note that there are probably various pesky
            # annoyances with our html approach, so let's solve
            # everything hand-wavily with html.escape
            cut = html.escape(cut)

            # First, format and screenshot the html using html2image.
            # We must also write this image to disk.
            # Note the first parameter in the format call.
            # It specifies that the bottom container display only if
            # we are up to the last cut.
            title_html = title_html_format.format(
                "flex" if i == len(self._text_cuts) - 1 else "none",
                utils.format_score(self.submission.score),
                self.submission.subreddit.icon_img,
                self.submission.subreddit.display_name,
                getattr(self.submission.author, "name", "anonymous"),
                cut
            )
            self.hti.screenshot(html_str=title_html, save_as="RedditTitleMediaFactory.tmphti.png")

            # Next, crop the image because html2image isn't perfect.
            title_image = Image.open(os.path.join(self.tmpdir.name, "RedditTitleMediaFactory.tmphti.png"))
            title_image = title_image.crop(title_image.getbbox())

            # Now, paste the image onto a blank background.
            # (26, 26, 27) are the RGB values corresponding to
            # hex color #1A1A1B, the comment background color.
            background = Image.new("RGB", (2560, 1440), (26, 26, 27))
            background.paste(title_image, (0, (background.height - title_image.height) // 2))

            # Finally, write the final image to disk.
            image_file = os.path.join(self.tmpdir.name, f"{self.submission.id}.{i}.png")
            background.save(image_file)
            image_files.append(image_file)

        return image_files

    def manufacture_audios(self) -> list[str]:
        audio_files = []

        # Load google text-to-speech client.
        # We are manufacturing mp3 files.
        client = texttospeech.TextToSpeechClient()
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        # Loop through all cuts.
        # We are saving each audio segment individually.
        for i, cut in enumerate(self._text_cuts):
            # We need to escape the html as to not confuse
            # Google Cloud's text-to-speech API.
            ssml = html.escape(cut)
            ssml = "<speak>" + ssml + "</speak>"

            # Let's synthesize our ssml and send our request to Google!
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=utils.random_voice_params(),
                audio_config=audio_config
            )

            # Now, let's write the response bytes to disk.
            audio_file = os.path.join(self.tmpdir.name, f"{self.submission.id}.{i}.mp3")
            with open(audio_file, "wb") as f:
                f.write(response.audio_content)
            audio_files.append(audio_file)

        return audio_files
