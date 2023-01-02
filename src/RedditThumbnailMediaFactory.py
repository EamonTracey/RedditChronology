import html
import os

from PIL import Image
import praw.models

from html_formats import title_html_format
from _HTIMediaFactory import _HTIMediaFactory
import utils


class RedditThumbnailMediaFactory(_HTIMediaFactory):
    def __init__(self, submission: praw.models.Submission):
        self.submission = submission

        super(RedditThumbnailMediaFactory, self).__init__()

    def manufacture_thumbnail(self, image_file: str = None) -> str:
        cut = html.escape(self.submission.title)

        title_html = title_html_format.format(
            "flex",
            utils.format_score(self.submission.score),
            self.submission.subreddit.icon_img,
            self.submission.subreddit.display_name,
            self.submission.author.name,
            cut
        )
        self.hti.screenshot(html_str=title_html, save_as="RedditThumbnailMediaFactory.tmphti.png")

        thumbnail_image = Image.open(os.path.join(self.tmpdir.name, "RedditThumbnailMediaFactory.tmphti.png"))
        thumbnail_image = thumbnail_image.crop(thumbnail_image.getbbox())

        background = Image.new("RGB", (2560, 1440), (26, 26, 27))
        background.paste(thumbnail_image, (0, (background.height - thumbnail_image.height) // 2))

        # Save the thumbnail to desired location.
        if image_file is None:
            image_file = f"{self.submission.id}.jpg"
        background.save(image_file)

        return image_file
