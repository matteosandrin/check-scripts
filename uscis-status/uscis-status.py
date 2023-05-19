from datetime import datetime
from lxml import html
import argparse
import requests
import os.path
import json
import sys
import re

parser = argparse.ArgumentParser(description="Check the status of a USCIS case")
parser.add_argument(
    "receipt_num",
    type=str,
    help="The receipt number of the USCIS case",
    metavar="receipt_num",
    nargs=1,
)
parser.add_argument(
    "label",
    type=str,
    help="The human-friendly name of the USCIS case",
    metavar="label",
    nargs=1,
)
args = parser.parse_args()
RECEIPT_NUMBER = args.receipt_num[0]
CASE_LABEL = args.label[0]

current_dir, _ = os.path.split(__file__)
URL = "https://egov.uscis.gov/casestatus/mycasestatus.do"
CONFIG_PATH = os.path.join(current_dir, "config.json")
EXAMPLE_CONFIG_PATH = os.path.join(current_dir, "config.example.json")
PREV_PATH = os.path.join(current_dir, "case_status_{}.json".format(RECEIPT_NUMBER))

if not os.path.exists(CONFIG_PATH):
    print("ERROR: config.json file not found", file=sys.stderr)
    if os.path.exists(EXAMPLE_CONFIG_PATH):
        print(
            "please rename 'config.example.json' to 'config.json' and fill in the config parameters",
            file=sys.stderr,
        )
    exit(1)

CONFIG = json.load(open(CONFIG_PATH))


def get_previous(path=PREV_PATH):
    if os.path.exists(path):
        return json.load(open(path))
    print("WARNING: did not find previous value. Returning empty")
    return [{"status": "", "description": ""}]


def write_current(data, path=PREV_PATH):
    history = []
    if os.path.exists(path):
        history = get_previous()
    history.append(data)
    file_ptr = open(path, "w")
    json.dump(history, file_ptr, indent=4)


def notify(message):
    params = {
        "token": CONFIG["pushover_token"],
        "user": CONFIG["pushover_user"],
        "message": message,
        "html": 1,
    }
    requests.post("https://api.pushover.net/1/messages.json", params=params)


print('Downloading "{}" ...'.format(URL))
response = requests.post(
    URL,
    data={
        "changeLocale": "",
        "completedActionsCurrentPage": "0",
        "upcomingActionsCurrentPage": "0",
        "appReceiptNum": RECEIPT_NUMBER,
        "caseStatusSearchBtn": "CHECK STATUS",
    },
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

tree = html.document_fromstring(response.text)
status_container = tree.cssselect(".uscis-seal > .appointment-sec > .rows.text-center")

if len(status_container) == 0:
    print("ERROR: could not find case status in page", file=sys.stderr)
    exit(1)

status_container = status_container[0]
status = status_container.cssselect("h1")[0].text_content().strip()
description = status_container.cssselect("p")[0].text_content().strip()
new_status = {
    "status": status,
    "description": description,
    "date": datetime.now().isoformat(),
}

history = get_previous()
old_status = history[-1]

print("old case status: \n{status}\n{description}\n".format(**old_status))
print("new case status: \n{status}\n{description}\n".format(**new_status))

if (
    old_status["status"] != new_status["status"]
    or old_status["description"] != new_status["description"]
):
    print("There is a new update!")
    write_current(new_status)
    message = """<b>Update on "{}": {}.</b> {}""".format(
        CASE_LABEL, new_status["status"], new_status["description"]
    )
    notify(message)
else:
    print("No update. Exiting!")
