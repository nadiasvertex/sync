import csv
import os
import sys

import argparse


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
    global args
    cmd = [
        sys.executable,
        "-m", "client",
        "--service=" + args.service,
        "sync-all", "annotation"
    ]
    cmd = " ".join(cmd)
    print(cmd)
    os.system(cmd)


parser = argparse.ArgumentParser(prog="test")
parser.add_argument(
    '--service', default='http://localhost:8080/',
    metavar="URL",
    help='The service address to connect to. Default is %(default)s')
args = parser.parse_args()

load_data("values-1.txt")
sync_data()
load_data("values-2.txt")
sync_data()
