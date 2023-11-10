import requests
import json
import sys
import os


def notify(message, token, user):
    params = {
        "token": token,
        "user": user,
        "message": message,
        "html": 1,
    }
    requests.post("https://api.pushover.net/1/messages.json", params=params)

def get_data_path():
    current_dir, _ = os.path.split(__file__)
    return os.path.join(current_dir, "data")

def get_previous_text(path):
    if os.path.exists(path):
        file_ptr = open(path)
        return file_ptr.read().strip()
    print("WARNING: did not fine previous date value. Returning empty")
    return ""

def get_previous_json(path, default):
    if os.path.exists(path):
        return json.load(open(path))
    print("WARNING: did not find previous value. Returning empty")
    return default


def create_output_dir():
    path = get_data_path()
    if not os.path.exists(path):
        os.makedirs(path)


def write_current_list(data, path):
    create_output_dir()
    prev = []
    if os.path.exists(path):
        prev = get_previous_json(path, [])
    prev.append(data)
    file_ptr = open(path, "w")
    json.dump(prev, file_ptr, indent=4)


def write_current_text(data, path):
    create_output_dir()
    file_ptr = open(path, "w")
    file_ptr.write(data)


def get_config(key):
    current_dir, _ = os.path.split(__file__)
    config_path = os.path.join(current_dir, "config.json")
    example_config_path = os.path.join(current_dir, "config.example.json")
    if not os.path.exists(config_path):
        print("ERROR: config.json file not found", file=sys.stderr)
        if os.path.exists(example_config_path):
            print(
                "please rename 'config.example.json' to 'config.json' and fill in the config parameters",
                file=sys.stderr,
            )
        exit(1)
    config = json.load(open(config_path))
    if key not in config:
        print("ERROR: Could not find config key \"{}\"".format(key))
        exit(1)
    return config[key]

def get_user_agent():
    return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
