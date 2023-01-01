from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo


class YouTubeUploader:
    def __init__(
            self,
            video_file: str,
            credentials: str,
            storage: str,
            /,
            *,
            thumbnail: str,
            title: str,
            description: str,
            tags: list[str] = None,
            category: str = "",
            default_language: str = "en-US",
            embeddable: bool = True,
            license_: str = "creativeCommon",
            privacy_status: str = "public",
            public_stats_viewable: bool = True,
    ):
        self.video_file = video_file
        self.thumbnail = thumbnail
        self.title = title
        self.description = description
        self.tags = tags
        self.category = category
        self.default_language = default_language
        self.embeddable = embeddable
        self.license = license_
        self.privacy_status = privacy_status
        self.public_stats_viewable = public_stats_viewable
        self.channel = self._login(credentials, storage)

    @staticmethod
    def _login(credentials: str, storage: str) -> Channel:
        channel = Channel()
        channel.login(credentials, storage)
        return channel

    def upload(self):
        video = LocalVideo(self.video_file)
        video.set_thumbnail_path(self.thumbnail)
        video.set_title(self.title)
        video.set_description(self.description)
        video.set_tags(self.tags or [])
        video.set_category(self.category)
        video.set_default_language(self.default_language)
        video.set_embeddable(self.embeddable)
        video.set_license(self.license)
        video.set_privacy_status(self.privacy_status)
        video.set_public_stats_viewable(self.public_stats_viewable)

        self.channel.upload_video(video)
