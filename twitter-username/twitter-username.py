from enum import Enum
import requests
import os.path
import json
import time
import sys

current_dir, _ = os.path.split(__file__)
CONFIG_PATH = os.path.join(current_dir, "config.json")
EXAMPLE_CONFIG_PATH = os.path.join(current_dir, "config.example.json")

if not os.path.exists(CONFIG_PATH):
    print("ERROR: config.json file not found", file=sys.stderr)
    if os.path.exists(EXAMPLE_CONFIG_PATH):
        print("please rename 'config.example.json' to 'config.json' and fill in the config parameters", file=sys.stderr)
    exit(1)

CONFIG = json.load(open(CONFIG_PATH))

class LookupResponse(Enum):
    UNKNOWN = 0
    RATE_LIMIT_EXCEEDED = 1
    USERNAME_TAKEN = 2
    USERNAME_AVAILABLE = 3
    USERNAME_SUSPENDED = 4

def lookup(username):
    url = "https://api.twitter.com/2/users/by"
    querystring = {
        "usernames": username,
        "user.fields": "created_at",
    }
    headers = {
        "Authorization": "Bearer {}".format(CONFIG["twitter_token"]),
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring
    )

    if response.status_code == 429:
        return LookupResponse.RATE_LIMIT_EXCEEDED

    data = response.json()

    try:
        if data["data"][0]["created_at"]:
            return LookupResponse.USERNAME_TAKEN
    except:
        error_code = data["errors"][0]
        if error_code["detail"].find("suspended") != -1:
            return LookupResponse.USERNAME_SUSPENDED
        if error_code["detail"].find("Could not find") != -1:
            return LookupResponse.USERNAME_AVAILABLE
    else:
        return LookupResponse.UNKNOWN

def notify(message):
    params = {
        "token" : "a8wxafngmhgsej1sp9imhgds4k9wwz",
        "user" : "uxcojf3rjqen1skrzaj1b5175wg9f3",
        "message" : message
    }
    requests.post("https://api.pushover.net/1/messages.json", params=params)

def lookupResponseEnumToString(e):
    if e == LookupResponse.USERNAME_TAKEN:
        return "taken"
    if e == LookupResponse.USERNAME_AVAILABLE:
        return "available"
    if e == LookupResponse.USERNAME_SUSPENDED:
        return "suspended"
    if e == LookupResponse.RATE_LIMIT_EXCEEDED:
        return "rate limit exceeded"
    else:
        return "unknown"


username_status = [
    ("msandrin", LookupResponse.USERNAME_TAKEN),
    ("masand", LookupResponse.USERNAME_TAKEN),
    ("msandr", LookupResponse.USERNAME_TAKEN),
    ("mattsa", LookupResponse.USERNAME_TAKEN),
    ("matteos", LookupResponse.USERNAME_SUSPENDED),
]
        
for username, old_status in username_status:
    print("Checking username \"{}\"...".format(username))
    new_status = lookup(username)
    if new_status == LookupResponse.RATE_LIMIT_EXCEEDED:
        print("Rate limit exceed. Aborting!")
        notify("Rate limit exceeded on the Twitter api")
        printf("ERROR: RATE_LIMIT_EXCEEDED", file=sys.stderr)
        exit(1)
    if new_status != old_status:
        print("New status!", new_status)
        notify("The username \"{}\" is now {}".format(
            username, lookupResponseEnumToString(new_status)))
    else:
        print(new_status)
    time.sleep(2)