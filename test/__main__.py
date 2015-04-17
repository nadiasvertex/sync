import csv
import os
import sys


def update_data(citation, note, pub, text_range):
    cmd = [
        sys.executable,
        "-m", "client",
        "set", "--pub=" + pub,
        "--citation=" + citation,
        "annotation"
    ]
    if text_range:
        cmd.append("--range=" + text_range)
    if note:
        cmd.append("--note=\"%s\"" % note)
    cmd = " ".join(cmd)
    print(cmd)
    os.system(cmd)


def load_data(filename):
    data_path = os.path.join(os.path.dirname(__file__), filename)
    with open(data_path, "r") as i:
        reader = csv.reader(i)
        for r in reader:
            pub, citation, text_range, note = r
            update_data(citation, note, pub, text_range)


def sync_data():
    cmd = [
        sys.executable,
        "-m", "client",
        "--service=http://localhost:9090",
        "sync-all", "annotation"
    ]
    cmd = " ".join(cmd)
    print(cmd)
    os.system(cmd)


load_data("values-1.txt")
sync_data()
load_data("values-2.txt")
sync_data()
