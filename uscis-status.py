from datetime import datetime
import argparse
import requests
import os.path
import util
import json
import time
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
RETRIES = 10

current_dir, _ = os.path.split(__file__)
URL_AUTH = "https://egov.uscis.gov/csol-api/ui-auth"
URL_STATUS = "https://egov.uscis.gov/csol-api/case-statuses/{}".format(RECEIPT_NUMBER)
URL_HISTORY = "https://egov.uscis.gov/csol-api/case-history/{}/english".format(RECEIPT_NUMBER)
config = util.get_config("uscis-status")

print('Checking "{}", receipt number {}'.format(CASE_LABEL, RECEIPT_NUMBER))
print('Downloading "{}" ...'.format(URL_STATUS))
response = None
for i in range(RETRIES):
    print("Attempt {} of {}".format(i+1, RETRIES))
    try:
        auth_response = requests.get(
            URL_AUTH,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
        )
        token = auth_response.json()["JwtResponse"]["accessToken"]
        response = requests.get(
            URL_STATUS,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token,
            },
        )
        break
    except Exception as e:
        print("There was an error: {}".format(e), file=sys.stderr)
        if (i == RETRIES-1):
            raise Exception("ERROR: too many retries")
        print("waiting and trying again...")
        time.sleep(10)

if response.status_code != 200:
    print(
        "ERROR: {} replied with status code {}".format(URL_STATUS, response.status_code),
        file=sys.stderr,
    )
    exit(1)

data = response.json()

new_status = {
    "status": data['CaseStatusResponse']['detailsEng']['actionCodeText'],
    "description": re.sub('<.*?>', '', data['CaseStatusResponse']['detailsEng']['actionCodeDesc']),
    "date": datetime.now().isoformat(),
}

prev_path = os.path.join(util.get_data_path(), "uscis-status-{}.json".format(RECEIPT_NUMBER))
history = util.get_previous_json(prev_path, [{
    "status" : "",
    "description" : ""
}])
old_status = history[-1]

print("old case status: \n{status}\n{description}\n".format(**old_status))
print("new case status: \n{status}\n{description}\n".format(**new_status))

if (
    old_status["status"] != new_status["status"]
    or old_status["description"] != new_status["description"]
):
    print("There is a new update!")
    util.write_current_list(new_status, prev_path)
    message = """<b>Update on "{}": {}.</b> {}""".format(
        CASE_LABEL, new_status["status"], new_status["description"]
    )
    util.notify(message, config["pushover_token"], config["pushover_user"])
else:
    print("No update. Exiting!")
