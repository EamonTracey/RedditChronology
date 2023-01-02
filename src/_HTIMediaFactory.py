import html2image

from _MediaFactory import _MediaFactory


class _HTIMediaFactory(_MediaFactory):
    def __init__(self):
        super(_HTIMediaFactory, self).__init__()

        self.hti = html2image.Html2Image(output_path=self.tmpdir.name)
