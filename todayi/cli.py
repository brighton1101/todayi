import argparse
import sys

from todayi.config import DEFAULT_CONFIG as default_config
from todayi.controller import Controller
from todayi.util.iter import is_iterable


description = """
todayi: Keep track of what you do today, and just forget about it.
Writes what you do, everyday, to a backend. Then, retrieve the results
later without having to remember a single thing.

Example usage:
`todayi "Figured out how to do xyz in GCP w terraform" -t gcp terraform xyz`.
Will produce an entry in your record with the date it was created,
 text with the description, and tag the entry with keywords gcp, terraform, and xyz.
"""


def set_default_subparser(self, name):
    """
    Set default subparser
    """
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in ["-h", "--help"]:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
        if not subparser_found:
            # insert default in last position before global positional
            # arguments, this implies no global options are specified after
            # first positional argument
            sys.argv.insert(1, name)


def run():
    filter_kwargs = Controller.filter_kwargs.keys()

    def add_filter_kwargs(sp):
        sp.add_argument(
            "-c",
            "--contains",
            dest="content_contains",
            help="Include entries with content that contains string pattern",
        )
        sp.add_argument(
            "-e",
            "--equals",
            dest="content_equals",
            help="Include entries with content that matches string pattern",
        )
        sp.add_argument(
            "-nc",
            "--not-contains",
            dest="content_not_contains",
            help="Include entries with content that doesn't contain string pattern",
        )
        sp.add_argument(
            "-ne",
            "--not-equals",
            dest="content_not_equals",
            help="Include entries with content that doesn't match string pattern",
        )
        sp.add_argument(
            "-a",
            "--after",
            dest="after",
            help="Show content after date pattern following: `mm/dd/YYYY`",
        )
        sp.add_argument(
            "-b",
            "--before",
            dest="before",
            help="Show content before date pattern following: `mm/dd/YYYY`",
        )
        sp.add_argument(
            "-wt",
            "--with-tags",
            dest="with_tags",
            help="Show content that has tags (Comma separated)",
        )
        sp.add_argument(
            "--without-tags",
            dest="without_tags",
            help="Show content without tags (Comma separated)",
        )

    def get_filter_kwargs(args):
        args = vars(args)
        return dict((k, v) for k, v in args.items() if k in filter_kwargs)

    argparse.ArgumentParser.set_default_subparser = set_default_subparser
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(dest="subcommand")

    # Remote
    remote_parser = subparsers.add_parser("remote")
    remote_parser.add_argument("option", nargs=1, help="Available: push, pull")
    remote_parser.add_argument(
        "-B",
        "--backup",
        action="store_true",
        help="Backup changes so they won't overwrite anything",
    )

    # Report
    valid_report_formats = [
        "md",
        "csv",
    ]
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument(
        "format",
        nargs=1,
        help="Format to use. Available: {}".format(valid_report_formats),
    )
    report_parser.add_argument(
        "-o",
        "--output-file",
        dest="output_file",
        default=None,
        required=True,
        help="Ouput file path (absolute) or gist name if using gist flag.",
    )
    report_parser.add_argument(
        "--gist",
        action="store_true",
        help="Create gist instead of local output. Note that output-file will become gist name.",  # noqa
    )
    report_parser.add_argument(
        "--public", action="store_true", help="If creating gist, make gist public."
    )
    add_filter_kwargs(report_parser)

    # Show
    show_parser = subparsers.add_parser(
        "show", help="Displays last several entries within terminal."
    )
    show_parser.add_argument(
        "-n", "--number", help="Number of entries to show", default=10
    )
    add_filter_kwargs(show_parser)

    # Config
    config_parser = subparsers.add_parser("config", help="Get and set config values")
    config_parser.add_argument("option", nargs=1, help="`get` or `set`")
    config_parser.add_argument(
        "config_name",
        nargs=1,
        help="Config key names. Available: {}".format(default_config.keys()),
    )
    config_parser.add_argument("value", nargs="?")

    # Default
    default_parser = subparsers.add_parser(
        "default",
        help="Default command. `todayi [content][tags]`. For more info `todayi default -h`",  # noqa
    )
    default_parser.add_argument(
        "content", nargs="*", help="Content of what you are trying to log you did."
    )
    default_parser.add_argument(
        "-t",
        "--tags",
        nargs="*",
        help="Single word identifying tags. Example `-t hello world` would leave the tags hello and world. Tags should only come after content",  # noqa
        default=[],
    )

    parser.set_default_subparser("default")
    args = parser.parse_args()

    cmd = args.subcommand

    controller = Controller()

    if cmd == "default":
        content = args.content
        tags = args.tags
        if is_iterable(content, allow_str=False):
            content = " ".join(content)
        controller.write_entry(content, tags)

    elif cmd == "show":
        display_max = args.number
        filter_kwargs = get_filter_kwargs(args)
        controller.print_entries(display_max=display_max, **filter_kwargs)

    elif cmd == "report":
        form = args.format[0]
        ofile = args.output_file
        gist = args.gist
        public = args.public
        filter_kwargs = get_filter_kwargs(args)
        if gist is True:
            controller.gist_report(form, ofile, public=public, **filter_kwargs)
        else:
            controller.file_report(form, ofile, **filter_kwargs)

    elif cmd == "config":
        opt = args.option[0]
        key = args.config_name[0]
        if opt == "get":
            print(controller.read_config(key))
        elif opt == "set":
            value = args.value
            controller.write_config(key, value)
        else:
            raise TypeError(
                "Invalid option for config {}. Valid: [get, set]".format(args.option)
            )

    elif cmd == "remote":
        opt = args.option[0]
        backup = args.backup
        if opt == "push":
            controller.push_remote(backup_remote=backup)
        elif opt == "pull":
            controller.pull_remote(backup_local=backup)
        else:
            raise TypeError(
                "Invalid option for remote {}. Valid: [push, pull]".format(args.option)
            )


if __name__ == "__main__":
    run()
