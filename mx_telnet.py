import re
import sys
import random
import string
import telnetlib

from time import sleep


class MailTelnetAdapter(telnetlib.Telnet):
    success_pattern = re.compile("^2[0-9]{2}.*")
    host_error_text = "Something went wrong when connecting to host! \n"
    global_error_text = "Something went wrong! \n"

    def __init__(self, host, loops_to_wait=5):
        self.host = host
        self.loops_to_wait = loops_to_wait
        super().__init__(host=host, port=25)
        self.say_hello()

    def write(self, *args, **kwargs):
        res = super().write(*args, **kwargs)
        sleep(0.5)
        return res

    def say_hello(self):
        self.write(b"helo hi\n")
        ok = self.check_responce_status()
        if not ok:
            sys.stdout.write(self.host_error_text)
        return

    def set_email_from(self):
        _from = self.random_mail_form_host()
        self.write("mail from: <{f}>\n".format(f=_from).encode())
        ok = self.check_responce_status()
        if not ok:
            sys.stdout.write(self.global_error_text)
        return

    def check_email(self, email):
        self.write("rcpt to: <{f}>\n".format(f=email).encode())
        res = self.check_responce_status()
        return res

    def random_mail_form_host(self):
        ch = "".join(random.choice(string.ascii_lowercase)
                     for _ in range(random.randint(7, 16)))
        nm = "".join(random.choice(string.digits)
                     for _ in range(random.randint(0, 4)))
        mail = ch + nm + "@" + self.host
        return mail

    def check_responce_status(self):
        res = self.read_from_socket_patiently()
        return self.responce_success(res)

    def read_from_socket_patiently(self):
        for i in range(self.loops_to_wait):
            res = self.read_very_eager().decode()
            if res:
                break
            sleep(0.2)
        return res

    def responce_success(self, res):
        return bool(re.match(self.success_pattern, res))
