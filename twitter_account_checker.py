# -*- coding: utf-8 -*-
"""
This module checks twitter accounts in order to detect if they were suspended or deleted.

Example
-------
    $ python twitter_account_checker.py twitter_username1 twitter_username2

"""
import sys
from optparse import OptionParser

try:
    from urllib.request import urlopen, Request
    from urllib.parse import quote
except ImportError:
    from urllib2 import Request, urlopen
    from urllib import quote
import requests


try:
    from joblib import Parallel, delayed
except ImportError:
    def Parallel(n_jobs):
        return lambda x: x

    def delayed(x): return x

getter = requests.Session()


def _list_to_delimited_string(str_list, delimiter=","):
    return delimiter.join(map(str, str_list))


def _two_dimensional_list_to_string(two_dim_list):
    str_list = [_list_to_delimited_string(row) for row in two_dim_list]
    return _list_to_delimited_string(str_list, "\n")


def _get_page_final_url(url):
    failed = 0
    while failed < 4:
        try:
            page = getter.head(url, allow_redirects='true')
            return page.url, page.status_code
        except requests.ConnectionError as e:
            print(e.message)
            print("Error, Try:" + str(failed) + " ,URL: " + url)
            failed += 1
    return None, None


def get_twitter_account_state(user_id):
    """This functions check for a twitter account its current state (Exist, Suspended, Not Found).

    Parameters
    ----------
    user_id str
        The username of the twitter account that should be checked.

    Returns
    -------
    tuple
        The username and its state (Exist, Suspended, Not Found).

    """
    url = _twitter_user_name_to_url(user_id)
    full_url = _get_page_final_url(url)
    if full_url[1] == 200:
        if "suspended" in full_url[0]:
            return user_id, "Suspended"
        else:
            return user_id, "Exist"
    elif full_url[1] == 404:
        return user_id, "Not Found"


def check_multiple_twitter_accounts(user_ids, workers=4):
    """This functions check a list of twitter accounts current state (Exist, Suspended, Not Found)

    Parameters
    ----------
    user_ids: list
        Contains list of usernames to check.
    workers int, optional
        If joblib installed determines the number of workers to use.

    Returns
    -------
    list[tuple]
        A list of that contains the states of the twitter accounts.
    """
    processes = Parallel(n_jobs=workers)(
        delayed(get_twitter_account_state)(user_id.rstrip()) for user_id in user_ids)
    processes = [x for x in processes if x is not None]
    return processes


def _twitter_user_name_to_url(username):
    return "https://twitter.com/" + username


if __name__ == '__main__':
    parser = OptionParser(usage='%prog [options] <twitter_username1> <twitter_username2> [<twitter_username3>...]')
    parser.add_option("--file", dest="file",
                      help="The path to the input file where each username in a separate line.", metavar="FILE")
    parser.add_option("--save", dest="output_path",
                      help="The path to the output file.")
    parser.add_option("--worker", dest="threads",
                      help="Number of workers to use when checking twitter accounts.", default=4)

    (options, ids) = parser.parse_args()
    accounts_states = []

    if ids:
        accounts_states = check_multiple_twitter_accounts(ids)
    elif options.file:
        with open(options.file, "r") as f:
            accounts_states = check_multiple_twitter_accounts(f, options.threads)
    if not ids and not options.file:
        parser.error("Please supply twitter usernames or a file.")
        sys.exit(1)

    csv = _two_dimensional_list_to_string(accounts_states)
    if options.output_path:
        with open(options.output_path, 'w') as f:
            f.write(csv)
    else:
        print(csv)

    sys.exit(1)
