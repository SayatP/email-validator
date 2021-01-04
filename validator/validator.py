import re
import sys
import random
from subprocess import getoutput
from collections import defaultdict
from validator.mx_telnet import MailTelnetAdapter


class EmailValidator:
    aggregated_emails = defaultdict(list)
    basic_email_pattern = re.compile("[^@\\s|\t]+@([^@\\s]+\\.[^@\\s]+)")
    bad_email_text = "{email} doensn't seem like a valid email, not gonna check \n"

    def __init__(self, emails):
        self.results = {}
        self.emails = emails

    def validate(self):
        [self._regex_check(email) for email in self.emails]
        hosts = {
            d: self.get_hosts_from_domain(d)
            for d in self.aggregated_emails.keys()
        }

        for domain, emails in self.aggregated_emails.items():
            clients = []
            for host in hosts[domain]:
                client = MailTelnetAdapter(host)
                client.set_email_from()
                clients.append(client)

            for mail in emails:
                cli = random.choice(clients)
                if random.randint(0, 20) < 3:
                    cli.set_email_from()
                res = cli.check_email(mail)
                self.results[mail] = res

        return self.results

    def _regex_check(self, email):
        match = re.match(self.basic_email_pattern, email)
        if not match:
            sys.stdout.write(self.bad_email_text.format(email=email))
            sys.stdout.flush()
        else:
            domain = match.groups()[0]
            self.aggregated_emails[domain].append(email)

    @staticmethod
    def get_hosts_from_domain(domain):
        def get_domain(host):
            return re.findall(".* exchanger = [0-9]* (.*?).$", host)[0]

        hosts = getoutput(f"nslookup -q=mx {domain}").split("\n")
        hosts = [get_domain(i) for i in hosts if "exchanger" in i]
        return hosts
