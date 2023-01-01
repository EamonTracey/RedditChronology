import itertools
import os
import random

import ffmpeg
import praw.models
from google.cloud import texttospeech

from _RedditCommentMediaFactory import _RedditCommentMediaFactory
from _RedditTitleMediaFactory import _RedditTitleMediaFactory
import utils


class RedditThreadMediaFactory:
    tmp = ".RedditThreadMediaFactory.tmp.{}.mp4"

    def __init__(
            self, submission: praw.models.Submission,
            auto: bool = True,
            n: int = 40,
            fps: float = 25,
            transition: tuple[str, str] = None
    ):
        self.submission = submission
        self.fps = fps
        self.n = n
        self.transition = transition

        # By default, praw does not load all comments at once.
        # However, we want to fetch all the comments.
        submission.comments.replace_more(limit=0)
        self.comments = submission.comments

        # If the user does not want the class to choose which comments to
        # include, we have to prompt the user for the relevant comments.
        self.relevant_comments = self._choose_relevant_comments() if auto else self._prompt_relevant_comments()

    def _choose_relevant_comments(self) -> list[praw.models.Comment]:
        return list(
            filter(
                lambda c: c.author is not None,
                self.comments[:self.n]
            )
        )

    def _prompt_relevant_comments(self) -> list[praw.models.Comment]:
        relevant_comments = []
        for i, comment in enumerate(self.comments):
            print(comment.body)

            while (query := input("Accept? ")) not in ["y", "n", "q"]:
                pass

            if query == "y":
                relevant_comments.append(comment)
                print("Accepted.\n")
            elif query == "n":
                print("Rejected.\n")
            elif query == "q":
                print("Rejected.\n")
                break

        return relevant_comments

    def manufacture_video(self, video_file: str = None) -> str:
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
        comment_factories = [
            _RedditCommentMediaFactory(
                comment,
                texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Standard-" + random.choice("ABCDEFGHIJ")
                )
            ) for comment in self.relevant_comments
        ]

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
        concatenator.output(self.tmp.format(i), r=self.fps, pix_fmt="yuv420p").run()
        # We are done if the number of streams is less than or equal to 32.
        # Otherwise, concatenate the rest of the streams to the mp4 in chunks.
        for i, streams_chunk in enumerate(utils.chunk(streams[32:], 32), start=1):
            mp4 = ffmpeg.input(self.tmp.format(i - 1))
            concatenator = ffmpeg.concat(mp4.video, mp4.audio, *streams_chunk, v=1, a=1)
            concatenator.output(self.tmp.format(i), r=self.fps, pix_fmt="yuv420p").run()
            os.remove(self.tmp.format(i - 1))

        # Save the file to desired location.
        if video_file is None:
            video_file = f"{self.submission.id}.mp4"
        os.rename(self.tmp.format(i), video_file)

        # Clean up temporary directories.
        # title_factory.cleanup()
        # for comment_factory in comment_factories:
        #     comment_factory.cleanup()

        return video_file
