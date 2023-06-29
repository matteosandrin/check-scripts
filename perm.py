import requests
import os.path
import util
import json
import sys
import re

current_dir, _ = os.path.split(__file__)
URL = "https://flag.dol.gov/processingtimes"

config = util.get_config("perm")

print('Downloading "{}" ...'.format(URL))
response = requests.get(
    URL,
    headers={
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    },
)

if response.status_code != 200:
    print(
        "ERROR: {} replied with status code {}".format(URL, response.status_code),
        file=sys.stderr,
    )
    exit(1)

re_result = re.search(
    r"PERM Processing Times.*(\d{1,2}\/\d{1,2}\/\d{4})", response.text
)

if re_result is None:
    print("ERROR: cannot find regular expression", file=sys.stderr)
    exit(1)

as_of_date = re_result.groups()[0]
prev_path = os.path.join(util.get_data_path(), "as_of_date.txt")
prev_as_of_date = util.get_previous_text(prev_path)

print("old as_of_date: {}".format(prev_as_of_date))
print("new as_of_date: {}".format(as_of_date))

if as_of_date != prev_as_of_date:
    util.write_current_text(as_of_date, prev_path)
    message = "The website {} has been updated!".format(URL)
    print(message)
    util.notify(message, config["pushover_token"], config["pushover_user"])
else:
    print("No update. Exiting!")
