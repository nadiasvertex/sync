import argparse
from pprint import pprint
import sys

import bookmarks


def add_options(parser, include_citation=False):
    parser.add_argument(
        "item_type", metavar="KIND", choices=("bookmark", "highlight"),
        help="Work with one of: %(choices)s."
    )
    parser.add_argument(
        "--slot",
        help="The bookmark slot to select."
    )
    parser.add_argument(
        "--pub", dest="pub", metavar="PUB",
        help="The publication to select (symbol:language)."
    )

    if include_citation:
        parser.add_argument(
            "--citation", dest="citation", metavar="CITATION",
            help="The bible (bible/book:chapter:verse) or document (doc/document_id:paragraph:offset) citation."
        )
        parser.add_argument(
            "--range", dest="range", metavar="CITATION RANGE",
            help="The bible range (bible/book:chapter:verse-book:chapter:verse) or "
                 "document range (doc/document_id:paragraph:offset-document_id:paragraph:offset) citation."
        )


def set_item(args):
    if args.item_type == "bookmark":
        bookmarks.set_bookmark(args.pub, args.slot, args.citation)


def del_item(args):
    if args.item_type == "bookmark":
        bookmarks.del_bookmark(args.pub, args.slot)


def get_item(args):
    if args.item_type == "bookmark":
        bookmarks.get_bookmarks(args.pub)


def sync_item(args):
    if args.item_type == "bookmark":
        bookmarks.sync_bookmarks(args.service, args.pub)


def sync_all_items(args):
    if args.item_type == "bookmark":
        r_status = bookmarks.get_bookmark_status(args.service, local=False)
        l_status = bookmarks.get_bookmark_status(args.service)
        pprint(r_status)
        pprint(l_status)
        if r_status["error"]:
            print("Failed to request bookmark status.")
            sys.exit(1)
        else:
            r_status = r_status["value"]

        r_index = {i["pub"]: i for i in r_status}
        l_index = {i["pub"]: i for i in l_status}

        pubs = set(r_index.keys()).union(set(l_index.keys()))
        for item in pubs:
            r_item = r_index.get(item)
            l_item = l_index.get(item)
            needs_update = \
                item not in l_index or \
                item not in r_index or \
                l_item.get("dirty", False) or \
                l_item.get("version", -1) < r_item.get("version")

            print("%s %s local=%s remote=%s" % (
                "*" if needs_update else " ",
                item,
                l_index.get(item, "not present"),
                r_index.get(item, "not present")
            ))
            if needs_update:
                bookmarks.sync_bookmarks(args.service, item)


parser = argparse.ArgumentParser(
    prog="client",
    epilog="A citation is always preceded with either bible/ or doc/ to "
           "indicate where it is being looked up. Note "
           "that you can specify partial citations for the end of a range. "
           "For example, bible/1:1:1-::5 means Genesis 1:1 to Genesis 1:5. It is "
           "also possible to omit the right hand components of a citation. They default "
           "to the first element, whatever that is. So, for example bible/1 means Genesis 1:1, "
           "where as doc/1231039 means the first character of the first paragraph of document id "
           "1231039."
)

parser.add_argument(
    '--service', default='http://localhost:8080/',
    metavar="URL",
    help='The service address to connect to. Default is %(default)s')

subparsers = parser.add_subparsers()
add = subparsers.add_parser("set", description="Set an item.")
add.set_defaults(func=set_item)
add_options(add, True)

delete = subparsers.add_parser("delete", description="Delete an item.")
delete.set_defaults(func=del_item)
add_options(delete)

get = subparsers.add_parser("get", description="Get an item.")
get.set_defaults(func=get_item)
add_options(get)

sync = subparsers.add_parser("sync", description="Synchronize an item.")
sync.set_defaults(func=sync_item)
add_options(sync)

sync_all = subparsers.add_parser("sync-all", description="Synchronize all items of the given type.")
sync_all.set_defaults(func=sync_all_items)
add_options(sync_all)

args = parser.parse_args()
args.func(args)
