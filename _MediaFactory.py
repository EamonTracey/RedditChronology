import tempfile


class _MediaFactory:
    def __init__(self):
        # Create a temporary directory in which to save intermediate files.
        self.tmpdir = tempfile.TemporaryDirectory()
