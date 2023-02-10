import requests
import os.path
import json
import sys
import re

current_dir, _ = os.path.split(__file__)
URL = "https://flag.dol.gov/processingtimes"
CONFIG_PATH = os.path.join(current_dir, "config.json")
EXAMPLE_CONFIG_PATH = os.path.join(current_dir, "config.example.json")
PREV_PATH = os.path.join(current_dir, "as_of_date.txt")

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
    print("WARNING: did not fine previous date value. Returning empty")
    return ""

def write_current(data, path=PREV_PATH):
    file_ptr = open(path, "w")
    file_ptr.write(data)

def notify(message):
    params = {
        "token" : CONFIG["pushover_token"],
        "user" : CONFIG["pushover_user"],
        "message" : message
    }
    requests.post("https://api.pushover.net/1/messages.json", params=params)


print("Downloading \"{}\" ...".format(URL))
response = requests.get(
    URL,
    headers={
        "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    })

if response.status_code != 200:
    print("ERROR: {} replied with status code {}".format(URL, response.status_code), file=sys.stderr)
    exit(1)

re_result = re.search(r"PERM Processing Times.*(\d{1,2}\/\d{1,2}\/\d{4})", response.text)

if re_result is None:
    print("ERROR: cannot find regular expression", file=sys.stderr)
    exit(1)

as_of_date = re_result.groups()[0]
prev_as_of_date = get_previous()

print("old as_of_date: {}".format(prev_as_of_date))
print("new as_of_date: {}".format(as_of_date))

if as_of_date != prev_as_of_date:
    write_current(as_of_date)
    message = "The website {} has been updated!".format(URL)
    print(message)
    notify(message)
else:
    print("No update. Exiting!")