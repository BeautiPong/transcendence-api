import smtplib
import ssl
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_silently = kwargs.get('fail_silently', False)
        self.debug_level = kwargs.get('debug_level', 0)

    def open(self):
        if self.connection:
            return False
        try:
            self.connection = smtplib.SMTP(
                self.host, self.port, timeout=self.timeout
            )
            self.connection.set_debuglevel(self.debug_level)

            if self.use_tls:
                self.connection.ehlo()
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.connection.starttls(context=context)
                self.connection.ehlo()

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise e
            return False
