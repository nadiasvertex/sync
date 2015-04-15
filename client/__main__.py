import argparse
import sys
from pprint import pprint

from client import bookmarks
from client import annotations


def add_options(parser, include_write_args=False):
    parser.add_argument(
        "item_type", metavar="KIND", choices=("bookmark", "annotation"),
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
    parser.add_argument(
        "--citation", dest="citation", metavar="CITATION",
        help="The bible (bible/book:chapter:verse) or document (doc/document_id:paragraph:offset) citation."
    )

    if include_write_args:
        parser.add_argument(
            "--range", dest="range", metavar="CITATION RANGE",
            help="The bible range (bible/book:chapter:verse-book:chapter:verse) or "
                 "document range (doc/document_id:paragraph:offset-document_id:paragraph:offset) citation."
        )
        parser.add_argument(
            "--note", dest="note", metavar="TEXT",
            help="A note to attach. If range is specified, the note will be attached to the range, otherwise "
                 "it will attach to the citation directly."
        )


def set_item(args):
    if args.item_type == "bookmark":
        bookmarks.set_bookmark(args.pub, args.slot, args.citation)
    elif args.item_type == "annotation":
        if args.range is None and args.note is not None:
            annotations.add_note(args.pub, args.citation, args.note)
        elif args.range is not None:
            annotations.add_highlight(args.pub, args.citation, args.range, args.note)
        else:
            print("You must specify at least --range or --note.")


def del_item(args):
    if args.item_type == "bookmark":
        bookmarks.del_bookmark(args.pub, args.slot)


def get_item(args):
    if args.item_type == "bookmark":
        bookmarks.get_bookmarks(args.pub)
    elif args.item_type == "annotation":
        annotations.get_annotations(args.pub, args.citation)


def sync_item(args):
    if args.item_type == "bookmark":
        bookmarks.sync_bookmarks(args.service, args.pub)
    elif args.item_type == "annotation":
        annotations.sync_annotations(args.service, args.pub, args.citation)


def sync_all_items(args):
    if args.item_type == "bookmark":
        bookmarks.sync_all_bookmarks(args.service)

    elif args.item_type == "annotation":
        annotations.sync_all_annotations(args.service)

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
