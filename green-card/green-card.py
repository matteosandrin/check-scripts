from lxml import html
import requests
import os.path
import json
import sys
import re

current_dir, _ = os.path.split(__file__)
URL = "https://egov.uscis.gov/casestatus/mycasestatus.do"
CONFIG_PATH = os.path.join(current_dir, "config.json")
EXAMPLE_CONFIG_PATH = os.path.join(current_dir, "config.example.json")
PREV_PATH = os.path.join(current_dir, "case_status.txt")

if not os.path.exists(CONFIG_PATH):
    print("ERROR: config.json file not found", file=sys.stderr)
    if os.path.exists(EXAMPLE_CONFIG_PATH):
        print("please rename 'config.example.json' to 'config.json' and fill in the config parameters", file=sys.stderr)
    exit(1)

CONFIG = json.load(open(CONFIG_PATH))

def get_previous(path=PREV_PATH):
    if os.path.exists(path):
        file_ptr = open(path)
        return file_ptr.read().strip()
    print("WARNING: did not fine previous value. Returning empty")
    return ""

def write_current(data, path=PREV_PATH):
    file_ptr = open(path, "w")
    file_ptr.write(data)

def notify(message):
    params = {
        "token" : CONFIG["pushover_token"],
        "user" : CONFIG["pushover_user"],
        "message" : message,
        "html" : 1
    }
    requests.post("https://api.pushover.net/1/messages.json", params=params)

print("Downloading \"{}\" ...".format(URL))
response = requests.post(
    URL,
    data={
        "changeLocale" : "",
        "completedActionsCurrentPage" : "0",
        "upcomingActionsCurrentPage" : "0",
        "appReceiptNum" : CONFIG["receipt_number"],
        "caseStatusSearchBtn" : "CHECK STATUS",
    },
    headers={
        "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    })

if response.status_code != 200:
    print("ERROR: {} replied with status code {}".format(URL, response.status_code), file=sys.stderr)
    exit(1)

tree = html.document_fromstring(response.text)
status_container = tree.cssselect(".uscis-seal > .appointment-sec > .rows.text-center")

if len(status_container) == 0:
    print("ERROR: could not find case status in page", file=sys.stderr)
    exit(1)

status_container = status_container[0]
status_short = status_container.cssselect("h1")[0].text_content().strip()
status_long = status_container.cssselect("p")[0].text_content().strip()

prev_case_status = get_previous()

print("old case status: {}".format(prev_case_status))
print("new case status: {}".format(status_short))

if status_short != prev_case_status:
    write_current(status_short)
    message = """<b>Updated green card status: {}.</b> {}""".format(
        status_short, status_long)
    print(status_short)
    print(status_long)
    notify(message)
else:
    print("No update. Exiting!")