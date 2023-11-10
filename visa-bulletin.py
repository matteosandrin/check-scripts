import requests
import util
from lxml import html
import re
import os.path

DOMAIN = "https://travel.state.gov"
URL = DOMAIN + "/content/travel/en/legal/visa-law0/visa-bulletin.html"
config = util.get_config("visa-bulletin")


def notify_new_visa_bulletin(bulletin_date, bulletin_url):
    prev_path = os.path.join(util.get_data_path(), "visa-bulletin.txt")
    prev_bulletin_date = util.get_previous_text(prev_path)

    print("old bulletin_date: {}".format(prev_bulletin_date))
    print("new bulletin_date: {}".format(bulletin_date))

    if bulletin_date != prev_bulletin_date:
        util.write_current_text(bulletin_date, prev_path)
        message = "New visa bulletin: {}\n{}".format(bulletin_date, bulletin_url)
        print(message)
        util.notify(message, config["pushover_token"], config["pushover_user"])
    else:
        print("No update. Exiting!")


print("Checking for a new visa bulletin...")
response = requests.get(URL, headers={"User-Agent": util.get_user_agent()})

if response.status_code != 200:
    print(
        "ERROR: {} replied with status code {}".format(URL, response.status_code),
        file=sys.stderr,
    )
    exit(1)

text = response.text
tree = html.fromstring(text)
recent_bulletins = tree.cssselect("#recent_bulletins > .current")[1]
recent_bulletins_text = recent_bulletins.text_content().strip()
match = re.search(r"[a-zA-Z]+[0-9]{4}", recent_bulletins_text)
if match is not None:
    bulletin_date = match.group()
    bulletin_url = DOMAIN + recent_bulletins.cssselect("a")[0].get("href")
    notify_new_visa_bulletin(bulletin_date, bulletin_url)
else:
    print("No update. Exiting!")
