class Email:
    def __init__(
        self,
        subject=None,
        recipient=None,
        message_body_file=None,
        _force_empty=False,
    ):
        self.subject = subject
        self.recipient = recipient
        self.message_body_file = message_body_file
        self.cmd = None

        if not _force_empty:
            self.prep_command()

    def prep_command(self):
        if self.recipient is None:  # Keep as None
            pass
        elif self.message_body_file is None:
            self.cmd = self._attachment_free()
        else:
            self.cmd = self._include_attachment()

    def _attachment_free(self):
        return ["echo", ""], [
            "mailx",
            "-s",
            self.subject.replace(" ", "-"),
            self.recipient,
        ]

    def _include_attachment(self):
        return ["cat", self.message_body_file.as_posix()], [
            "mailx",
            "-s",
            self.subject.replace(" ", "-"),
            self.recipient,
        ]

    def get_command(self):
        return self.cmd

    @classmethod
    def null(cls):
        return cls(_force_empty=True)
