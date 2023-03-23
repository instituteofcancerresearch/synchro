from synchro.utils.emails import Email
from synchro.utils.paths import Path


class TestEmailClass:
    subject = "subject"
    address = "user@place.com"
    attachment = "test_mail_content.txt"

    email_no_attachment = Email(subject, address)
    email_inc_attachment = Email(subject, address, Path(attachment))
    email_null = Email.null()

    def test_no_attachment(self):
        echo_cmd, mail_cmd = self.email_no_attachment.get_command()

        assert echo_cmd[0] == "echo"
        assert echo_cmd[1] == ""

        assert mail_cmd[0] == "mailx"
        assert mail_cmd[1] == "-s"
        assert mail_cmd[2] == self.subject
        assert mail_cmd[3] == self.address

    def test_inc_attachement(self):
        cat_cmd, mail_cmd = self.email_inc_attachment.get_command()

        assert cat_cmd[0] == "cat"
        assert cat_cmd[1] == self.attachment

        assert mail_cmd[0] == "mailx"
        assert mail_cmd[1] == "-s"
        assert mail_cmd[2] == self.subject
        assert mail_cmd[3] == self.address

    def test_null(self):
        cmd = self.email_null.get_command()

        assert cmd is None
