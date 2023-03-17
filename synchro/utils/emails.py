class Email:
    def __init__(self, subject=None, recipient=None, attachment=None, _force_empty=False):
        self.subject = subject
        self.recipient = recipient
        self.attachment = attachment
        self.cmd = []

        if not _force_empty:
            self.prep_command()

    def prep_command(self):
        if self.attachment is None:
            self.cmd = self._attachment_free()
        else:
            self.cmd = self._include_attachment()

    def _attachment_free(self):
        return ["mailx", "-s", self.subject, self.recipient]

    def _include_attachment(self):
        return [
            "uuencode",
            "file",
            self.attachment,
            "|",
            "mailx",
            "-s",
            self.subject,
            self.recipient,
        ]

    def get_command(self):
        return self.cmd

    @classmethod
    def null(cls):
        return cls(_force_empty=True)
