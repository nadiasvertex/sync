import argparse

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

args = parser.parse_args()
args.func(args)
