import itertools
import html
import os
import random

from PIL import Image
import praw.models
from google.cloud import texttospeech

from _TextMediaFactory import _TextMediaFactory
import utils


class _RedditCommentMediaFactory(_TextMediaFactory):
    # These hex codes correspond to background colors for default reddit avatars.
    # They are present in URLs that return default reddit avatar images.
    avatar_colors = ["0079D3", "0DD3BB", "24A0ED", "FF4500", "FF8717", "FFB000"]

    # This string is html that displays a Reddit comment,
    # or at least my best recreation of a Reddit comment.
    # The string should be formatted with 4 parameters:
    # 1) display bottom container 2) pfp url 3) username 4) comment 5) score.
    comment_html_format = """<style>.root{{background:#1a1a1b;padding:1em;font-family:sans-serif;font-size:1.25em;max-width:1080px;}}.top-container{{display:flex;align-items:center;gap:.35em}}.avatar{{border-radius:50%;height:2em;width:2em}}.username{{color:#d7dadc}}.ago{{font-size:.75em;color:#818384}}.line{{margin-left:1em;border-left:2px solid gray}}.middle-container{{display:flex;margin-top:.5em;margin-left:1em}}.comment{{color:#d7dadc;margin-left:.35em}}.bottom-container{{display:{};align-items:center;margin-top:1em;margin-left:1.35em;gap:.5em;color:#818384}}@font-face{{font-family:vote;src:url(https://www.redditstatic.com/desktop2x/fonts/redesignIcon2020/redesignFont2020.a59e78115daeedbd9ef7f241a25c2031.ttf)}}.icon{{font-family:vote;font-size:1.2em}}.upvote-icon:before{{content:"\\f34c"}}.votes{{color:#d7dadc}}.downvote-icon:before{{content:"\\f197"}}.comment-icon:before{{content:"\\f16f"}}.option{{font-size:.75em}}</style><div class=root><div class=top-container><img class=avatar src={}><div class=username>{}</div><div class=ago>·</div><div class=ago>sometime ago</div></div><div class=line><div class=middle-container><div class=comment>{}</div></div><div class=bottom-container><div class="icon upvote-icon"></div><div class=votes>{}</div><div class="icon downvote-icon"></div><div class="icon comment-icon"></div><div class=option><b>Reply</b></div><div class=option><b>Give Award</b></div><div class=option><b>Share</b></div><div class=option><b>Report</b></div><div class=option><b>Save</b></div><div class=option><b>Follow</b></div></div></div></div>"""

    # This file will be used as a temporary file
    # for saving images with html2image.
    tmp = "._RedditCommentMediaFactory.tmp.png"

    def __init__(
            self,
            comment: praw.models.Comment,
            pdir: str,
            voice_params: texttospeech.VoiceSelectionParams = None,
            use_default_avatar: bool = False,
    ):
        self.comment = comment
        self.use_default_avatar = use_default_avatar

        super(_RedditCommentMediaFactory, self).__init__(self.comment.body, pdir, voice_params)

    @classmethod
    def randavatarurl(cls):
        def randavatar() -> str:
            return "https://www.redditstatic.com/avatars/avatar_default_{:2d}_{}.png".format(
                random.randint(1, 20),
                random.choice(cls.avatar_colors)
            )

    def manufacture_images(self) -> list[str]:
        ifiles = []

        # Either use the commenter's actual profile picture,
        # or use a random default avatar.
        # We use getattr since icon_img will not be a valid attribute
        # for suspended/banned accounts according to PRAW documentation.
        # We then fall back to a random default avatar.
        pfp_url = self.randavatarurl() if self.use_default_avatar else \
            getattr(self.comment.author, "icon_img", self.randavatarurl())

        # Loop through the accumulation of cuts.
        # We want to save an image of the comment
        # with each cut and its preceding text.
        for i, cut in enumerate(itertools.accumulate(self.text_cuts)):
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
            comment_html = self.comment_html_format.format(
                "flex" if i == len(self.text_cuts) - 1 else "none",
                pfp_url,
                self.comment.author.name,
                cut,
                utils.format_score(self.comment.score)
            )
            self.hti.screenshot(html_str=comment_html, save_as=self.tmp)

            # Next, crop the image because html2image isn't perfect.
            comment_img = Image.open(self.tmp)
            os.remove(self.tmp)
            comment_img = comment_img.crop(comment_img.getbbox())

            # Now, paste the image onto a blank background.
            # (26, 26, 27) are the RGB values corresponding to
            # hex color #1A1A1B, the comment background color.
            bg = Image.new("RGB", (2560, 1440), (26, 26, 27))
            bg.paste(comment_img, (0, (bg.height - comment_img.height) // 2))

            # Finally, write the final image to disk.
            ifile = f"{self.pdir}/{self.comment.id}.{i}.png"
            bg.save(ifile)
            ifiles.append(ifile)

        return ifiles

    def manufacture_audios(self) -> list[str]:
        afiles = []

        # Load google text-to-speech client.
        # We are manufacturing mp3 files.
        client = texttospeech.TextToSpeechClient()
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        # Loop through all cuts.
        # We are saving each audio segment individually.
        for i, cut in enumerate(self.text_cuts):
            # We need to escape the html as to not confuse
            # Google Cloud's text-to-speech API.
            ssml = html.escape(cut)
            ssml = "<speak>" + ssml + "</speak>"

            # Let's synthesize our ssml and send our request to Google!
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice_params,
                audio_config=audio_config
            )

            # Now, let's write the response bytes to disk.
            afile = f"{self.pdir}/{self.comment.id}.{i}.mp3"
            with open(afile, "wb") as f:
                f.write(response.audio_content)
            afiles.append(afile)

        return afiles
