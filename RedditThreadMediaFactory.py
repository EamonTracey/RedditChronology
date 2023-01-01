import itertools
import os

import ffmpeg
import praw.models

from _RedditCommentMediaFactory import _RedditCommentMediaFactory
from _MediaFactory import _MediaFactory
from _RedditTitleMediaFactory import _RedditTitleMediaFactory
import utils


class RedditThreadMediaFactory(_MediaFactory):
    def __init__(self, submission: praw.models.Submission, fps: float = 25, transition: tuple[str, str] = None):
        self.submission = submission
        self.fps = fps
        self.transition = transition

        # By default, praw does not load all comments at once.
        # However, we want to fetch all the comments.
        submission.comments.replace_more(limit=0)
        self.comments = submission.comments

        super(RedditThreadMediaFactory, self).__init__()

    def manufacture_video(self, video_file: str = None, comments: list[praw.models.Comment] = None) -> str:
        streams = []

        # First, let's manufacture the title.
        title_factory = _RedditTitleMediaFactory(self.submission)
        title_image_files = title_factory.manufacture_images()
        title_audio_files = title_factory.manufacture_audios()

        # Then, create the ffmpeg input streams for the title.
        # View comment below to understand how we calculate framemrate.
        streams.extend(
            itertools.chain.from_iterable(
                (
                    ffmpeg.input(image_file, framerate=1 / (mlen := utils.media_duration(audio_file)), t=mlen),
                    ffmpeg.input(audio_file)
                )
                for image_file, audio_file in zip(title_image_files, title_audio_files)
            )
        )

        # Add optional transition.
        if self.transition is not None:
            streams.extend(
                map(ffmpeg.input, self.transition)
            )

        # Let's create a comment media factory for each comment.
        # We will use a random English (US) voice from Google's API.
        if comments is None:
            comments = self.comments
        comment_factories = [_RedditCommentMediaFactory(comment) for comment in comments]

        # Welcome to the meat of our operation.
        # We want to manufacture the image and audio files for each comment.
        # Then, we will create the ffmpeg input streams for each comment.
        for comment_factory in comment_factories:
            comment_ifiles = comment_factory.manufacture_images()
            comment_afiles = comment_factory.manufacture_audios()

            # Since we are generating videos from singular images,
            # we want the image to play for as long as its
            # corresponding audio.
            # Thus, we set the framerate to 1/(audio duration)
            # and ffmpeg's t to the audio duration.
            # We do nothing special to the audio.
            streams.extend(
                itertools.chain.from_iterable(
                    (
                        ffmpeg.input(ifile, framerate=1 / (mlen := utils.media_duration(afile)), t=mlen),
                        ffmpeg.input(afile),
                    )
                    for ifile, afile in zip(comment_ifiles, comment_afiles)
                )
            )

            # Add optional transition.
            if self.transition is not None:
                streams.extend(
                    map(ffmpeg.input, self.transition)
                )

        # Now, let's concatenate the streams.
        tmpmp4 = os.path.join(self.tmpdir.name, "RedditThreadMediaFactory.tmp.{}.mp4")
        # The naive approach is to simply concatenate everything at once.
        # However, since it is likely we must concatenate hundreds or
        # even thousands of files, it is likely ffmpeg will fail.
        # Mainstream operating systems limit how many file descriptors
        # can be opened at once. So, let's break up concatenation into chunks.
        # We will reasonably use chunks of size 32.
        # First, create the mp4 file with the first up to 32 streams.
        # v=1 sets one output video stream.
        # a=1 sets one output audio stream.
        i = 0
        concatenator = ffmpeg.concat(*streams[0:32], a=1, v=1)
        # We set the pixel format to yuv420p so that more
        # media players (e.g., QuickTime) support our mp4.
        concatenator.output(tmpmp4.format(i), r=self.fps, pix_fmt="yuv420p").run()
        # We are done if the number of streams is less than or equal to 32.
        # Otherwise, concatenate the rest of the streams to the mp4 in chunks.
        for i, streams_chunk in enumerate(utils.chunk(streams[32:], 32), start=1):
            mp4 = ffmpeg.input(tmpmp4.format(i - 1))
            concatenator = ffmpeg.concat(mp4.video, mp4.audio, *streams_chunk, v=1, a=1)
            concatenator.output(tmpmp4.format(i), r=self.fps, pix_fmt="yuv420p").run()
            os.remove(tmpmp4.format(i - 1))

        # Save the file to desired location.
        if video_file is None:
            video_file = f"{self.submission.id}.mp4"
        os.rename(tmpmp4.format(i), video_file)

        return video_file
