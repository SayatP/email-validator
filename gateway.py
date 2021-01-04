import re
import sys
import random
import argparse
from time import sleep
from subprocess import getoutput
from collections import defaultdict
from mx_telnet import MailTelnetAdapter

parser = argparse.ArgumentParser(description="Verify given emails.")
parser.add_argument(
    "--mails",
    type=str,
    nargs=1,
    required=True,
    metavar="mail1, mail2, mail3",
    help="list of mails to be verified separated by commas",
)


def get_hosts_from_domain(domain):
    def get_domain(host):
        return re.findall(".* exchanger = [0-9]* (.*?).$", host)[0]

    hosts = getoutput(f"nslookup -q=mx {domain}").split("\n")
    hosts = [get_domain(i) for i in hosts if "exchanger" in i]
    return hosts


args = parser.parse_args()
mails = args.mails[0].split(",")
basic_mail_pattern = re.compile("[^@\\s|\t]+@([^@\\s]+\\.[^@\\s]+)")
bad_mail_text = "{mail} doensn't seem like a valid email, not gonna check \n"
aggregated_mails = defaultdict(list)

for mail in mails:
    match = re.match(basic_mail_pattern, mail)
    if not match:
        sys.stdout.write(bad_mail_text.format(mail=mail))
        sys.stdout.flush()
    else:
        domain = match.groups()[0]
        aggregated_mails[domain].append(mail)

hosts = {d: get_hosts_from_domain(d) for d in aggregated_mails.keys()}

results = {}

for domain, mails in hosts.items():
    clients = []
    for host in hosts[domain]:
        client = MailTelnetAdapter(host)
        client.set_email_from()
        clients.append(client)

    for mail in aggregated_mails[domain]:
        cur = random.choice(clients)
        if random.randint(0, 20) < 3:
            cur.set_email_from()
        res = cur.check_email(mail)
        results[mail] = res

for k, v in results.items():
    sleep(0.2)
    sys.stdout.write(f"{k} is {'valid' if v else 'probably invalid'} \n")
