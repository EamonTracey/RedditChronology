import itertools
import html
import os
import random

from PIL import Image
import praw.models
from google.cloud import texttospeech

from html_formats import comment_html_format
from _HTIMediaFactory import _HTIMediaFactory
import utils


class _RedditCommentMediaFactory(_HTIMediaFactory):
    # These hex codes correspond to background colors for default reddit avatars.
    # They are present in URLs that return default reddit avatar images.
    avatar_colors = ["0079D3", "0DD3BB", "24A0ED", "FF4500", "FF8717", "FFB000"]

    def __init__(self, comment: praw.models.Comment):
        self.comment = comment
        self._text_cuts = utils.text_cuts(self.comment.body)

        super(_RedditCommentMediaFactory, self).__init__()

    @classmethod
    def randavatarurl(cls):
        return "https://www.redditstatic.com/avatars/avatar_default_{:2d}_{}.png".format(
            random.randint(1, 20),
            random.choice(cls.avatar_colors)
        )

    def manufacture_images(self) -> list[str]:
        image_files = []

        # Either use the commenter's actual profile picture,
        # or use a random default avatar.
        # We use getattr since icon_img will not be a valid attribute
        # for suspended/banned accounts according to PRAW documentation.
        # We then fall back to a random default avatar.
        pfp_url = getattr(self.comment.author, "icon_img", self.randavatarurl())

        # Loop through the accumulation of cuts.
        # We want to save an image of the comment
        # with each cut and its preceding text.
        for i, cut in enumerate(itertools.accumulate(self._text_cuts)):
            # Note that there are probably various pesky
            # annoyances with our html approach, so let's solve
            # everything hand-wavily with html.escape
            cut = html.escape(cut)
            # However, since we are formatting text into html, we should
            # replace newline characters with html line breaks.
            cut = cut.replace("\n", "<br/>")

            # First, format and screenshot the html using html2image.
            # We must also write this image to disk.
            # Note the first parameter in the format call.
            # It specifies that the bottom container display only if
            # we are up to the last cut.
            comment_html = comment_html_format.format(
                "flex" if i == len(self._text_cuts) - 1 else "none",
                pfp_url,
                getattr(self.comment.author, "name", "anonymous"),
                cut,
                utils.format_score(self.comment.score)
            )
            self.hti.screenshot(html_str=comment_html, save_as="RedditCommentMediaFactory.tmphti.png")

            # Next, crop the image because html2image isn't perfect.
            comment_image = Image.open(os.path.join(self.tmpdir.name, "RedditCommentMediaFactory.tmphti.png"))
            comment_image = comment_image.crop(comment_image.getbbox())

            # Now, paste the image onto a blank background.
            # (26, 26, 27) are the RGB values corresponding to
            # hex color #1A1A1B, the comment background color.
            background = Image.new("RGB", (2560, 1440), (26, 26, 27))
            background.paste(comment_image, (0, (background.height - comment_image.height) // 2))

            # Finally, write the final image to disk.
            image_file = os.path.join(self.tmpdir.name, f"{self.comment.id}.{i}.png")
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
            audio_file = os.path.join(self.tmpdir.name, f"{self.comment.id}.{i}.mp3")
            with open(audio_file, "wb") as f:
                f.write(response.audio_content)
            audio_files.append(audio_file)

        return audio_files
