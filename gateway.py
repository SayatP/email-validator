import sys
import argparse
from time import sleep
from validator import EmailValidator

parser = argparse.ArgumentParser(description="Verify given emails.")
parser.add_argument(
    "--emails",
    type=str,
    nargs=1,
    required=True,
    metavar="mail1, mail2, mail3",
    help="list of emails to be verified separated by commas",
)

args = parser.parse_args()
emails = args.emails[0].split(",")


validator = EmailValidator(emails)
results = validator.validate()

for k, v in results.items():
    sleep(0.2)
    sys.stdout.write(f"{k} is {'valid' if v else 'most likely invalid'} \n")
