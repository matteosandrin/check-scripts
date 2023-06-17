import requests
import argparse
import os.path
import json
import sys

"""
Example usage:
python3 movie-tickets.py
    --theater_id=2a38ae86-dd3b-4d8f-9796-7ee0f443ec6e
    --event_id=6c1da7f4-4970-4f16-a310-cc4b6a7d325e
    --desired_seats H7 H6 H5 G7 G6 G5 F7 F6 F5
"""

parser = argparse.ArgumentParser(
    description="Check if your desired movies seats are available"
)
parser.add_argument(
    "--theater_id",
    type=str,
    help="The ID of the movie theater",
    nargs=1,
)
parser.add_argument(
    "--event_id",
    type=str,
    help="The ID of the film showing",
    nargs=1,
)
parser.add_argument(
    "--desired_seats",
    type=str,
    help="A list of desired seats",
    action="append",
    nargs="+",
)
args = parser.parse_args()

current_dir, _ = os.path.split(__file__)
URL = "https://booking.landmarktheatres.com/api/StartTicketing/{}/{}".format(
    args.theater_id[0], args.event_id[0]
)
DESIRED_SEATS = set(args.desired_seats[0])
CONFIG_PATH = os.path.join(current_dir, "config.json")
EXAMPLE_CONFIG_PATH = os.path.join(current_dir, "config.example.json")

print("Desired seats are: {}".format(", ".join(DESIRED_SEATS)))

if not os.path.exists(CONFIG_PATH):
    print("ERROR: config.json file not found", file=sys.stderr)
    if os.path.exists(EXAMPLE_CONFIG_PATH):
        print(
            "please rename 'config.example.json' to 'config.json' and fill in the config parameters",
            file=sys.stderr,
        )
    exit(1)

CONFIG = json.load(open(CONFIG_PATH))


def notify(message):
    params = {
        "token": CONFIG["pushover_token"],
        "user": CONFIG["pushover_user"],
        "message": message,
    }
    requests.post("https://api.pushover.net/1/messages.json", params=params)


print('Downloading "{}" ...'.format(URL))
response = requests.post(
    URL,
    headers={
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    },
    json={"selectedLanguageCulture": None},
)

if response.status_code != 200:
    print(
        "ERROR: {} replied with status code {}".format(URL, response.status_code),
        file=sys.stderr,
    )
    exit(1)

if response.headers["content-type"].find("application/json") == -1:
    print(
        "ERROR: response type is not JSON ({})".format(
            response.headers["content-type"]
        ),
        file=sys.stderr,
    )
    exit(1)

seating_data = response.json()
seating_data = seating_data["seatsViewModel"]["seatsLayoutModel"]

available_seats = set()
for row in seating_data["rows"]:
    if row["physicalName"] and len(row["physicalName"]) > 0:
        for seat in row["seats"]:
            if seat["type"] and (not seat["isUnavailable"]):
                available_seats.add(seat["seatName"])

available_desired_seats = available_seats.intersection(DESIRED_SEATS)

if len(available_desired_seats) > 0:
    message = "Some of the desired movie seats are available: {}".format(
        ", ".join(available_desired_seats)
    )
    print(message)
    notify(message)
else:
    print("NONE of the desired movie seats are availabe. Exit!")
