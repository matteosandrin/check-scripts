import requests
import os.path
import json
import sys
import re

current_dir, _ = os.path.split(__file__)
CONFIG_PATH = os.path.join(current_dir, "config.json")
URL = "https://us.urbanexcess.com/products/le-laboureur-moleskin-work-jacket-navy?variant=33058542217"

if not os.path.exists(CONFIG_PATH):
    print("ERROR: config.json file not found", file=sys.stderr)
    exit(1)

CONFIG = json.load(open(CONFIG_PATH))

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

re_sold_out = re.search(r"<button.*ProductForm__AddToCart.*Sold Out", response.text)
re_available = re.search(r"<button.*ProductForm__AddToCart.*Add to basket", response.text)

if (re_sold_out is None) and (re_available is None):
    print("ERROR: neither \"sold out\" or \"available\" regular expressions were matched", file=sys.stderr)
    exit(1)
if (re_sold_out is not None) and (re_available is not None):
    print("ERROR: both \"sold out\" and \"available\" regular expressions were matched", file=sys.stderr)
    exit(1)

if re_sold_out is not None:
    print("The chore coat is still sold out :(")
if re_available is not None:
    message = "The chore coat is now available! {}".format(URL)
    print(message)
    notify(message)
