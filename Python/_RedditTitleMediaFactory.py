import html
import itertools
import os

import praw.models
from PIL import Image
from google.cloud import texttospeech

from _TextMediaFactory import _TextMediaFactory
import utils


class _RedditTitleMediaFactory(_TextMediaFactory):
    # This string is html that displays a Reddit title,
    # or at least my best recreation of a Reddit title.
    # The string should be formatted with 4 parameters:
    # 1) display bottom container 2) score 3) icon url 4) subreddit name 5) username 6) title
    title_html_format = """<style>.root{{background:#1a1a1b;padding:1em;font-family:sans-serif;font-size:2em;max-width:1080px}}.encompassing-container{{display:flex}}.left-container{{display:flex;flex-direction:column;align-items:center;color:#818384;font-size:1em;gap:.2em}}@font-face{{font-family:vote;src:url(https://www.redditstatic.com/desktop2x/fonts/redesignIcon2020/redesignFont2020.a59e78115daeedbd9ef7f241a25c2031.ttf)}}.icon{{font-family:vote;font-size:1.2em}}.upvote-icon:before{{content:"\\f34c"}}.votes{{color:#d7dadc}}.downvote-icon:before{{content:"\\f197"}}.right-container{{margin-left:.75em}}.top-container{{display:flex;align-items:center;font-size:.65em;gap:.35em}}.avatar{{border-radius:50%;height:2em;width:2em}}.subreddit{{color:#d7dadc;font-weight:700}}.ago{{color:#818384}}.middle-container{{display:flex;margin-top:.5em}}.title{{color:#d7dadc;font-size:1.25em}}.bottom-container{{display:{};color:#818384;margin-top:1em;align-items:center;gap:.35em}}.comment-icon:before{{content:"\\f16f"}}.award-icon:before{{content:"\\f123"}}.share-icon:before{{content:"\\f280"}}.ellipsis-icon:before{{content:"\\f229"}}.option{{font-size:.75em;margin-right:1em;font-weight:700}}</style><div class=root><div class=encompassing-container><div class=left-container><div class="icon upvote-icon"></div><div class=votes>{}</div><div class="icon downvote-icon"></div></div><div class=right-container><div class=top-container><img class=avatar src={}><div class=subreddit>r/{}</div><div class=ago>·</div><div class=ago>Posted by u/{}</div></div><div class=middle-container><div class=title>{}</div></div><div class=bottom-container><div class="icon comment-icon"></div><div class=option>Comment</div><div class="icon award-icon"></div><div class=option>Award</div><div class="icon share-icon"></div><div class=option>Share</div><div class="icon ellipsis-icon"></div></div></div></div></div>"""

    # This file will be used as a temporary file
    # for saving images with html2image.
    tmp = "._RedditTitleMediaFactory.tmp.png"

    def __init__(
            self,
            submission: praw.models.Submission,
            pdir: str,
            voice_params: texttospeech.VoiceSelectionParams = None
    ):
        self.submission = submission

        super(_RedditTitleMediaFactory, self).__init__(self.submission.title, pdir, voice_params)

    def manufacture_images(self) -> list[str]:
        ifiles = []

        for i, cut in enumerate(itertools.accumulate(self.text_cuts)):
            # Note that there are probably various pesky
            # annoyances with our html approach, so let's solve
            # everything hand-wavily with html.escape
            cut = html.escape(cut)

            # First, format and screenshot the html using html2image.
            # We must also write this image to disk.
            # Note the first parameter in the format call.
            # It specifies that the bottom container display only if
            # we are up to the last cut.
            title_html = self.title_html_format.format(
                "flex" if i == len(self.text_cuts) - 1 else "none",
                utils.format_score(self.submission.score),
                self.submission.subreddit.icon_img,
                self.submission.subreddit.display_name,
                self.submission.author.name,
                cut
            )
            self.hti.screenshot(html_str=title_html, save_as=self.tmp)

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
            ifile = f"{self.pdir}/{self.submission.id}.{i}.png"
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
            afile = f"{self.pdir}/{self.submission.id}.{i}.mp3"
            with open(afile, "wb") as f:
                f.write(response.audio_content)
            afiles.append(afile)

        return afiles
