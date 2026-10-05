"""Command-line interface.

A thin layer over the public API: it reads arguments, calls the API, and
prints. Results go to standard output, errors to standard error.

Exit codes: 0 on success, 1 when the conversion fails (bad number, unknown or
unsupported unit, incompatible units), 2 for wrong command-line usage.
"""

import argparse
import sys
import textwrap
from collections.abc import Sequence

from unitconverter import api

_MARGIN = " " * 7
_USAGE = f"%(prog)s -v VALUE --from UNIT --to UNIT\n{_MARGIN}%(prog)s [-h | -l]"

_PROG_NAME = "unitconverter"
_EXAMPLES = f"""\
examples:
  {_PROG_NAME} -v 10 km miles
  {_PROG_NAME} --value 100 celsius fahrenheit
  {_PROG_NAME} -v 5 "nautical mile" km
  {_PROG_NAME} -v=-1e3 m km

Unit names ignore case and accept symbols, plurals and British spellings.
Put names with spaces in quotes. And use the equality when dealing with
negative numbers.
"""

_LIST_WIDTH = 78


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog=f"{_PROG_NAME}",
        usage=_USAGE,
        description="Convert a value from one unit to another.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--value",
        help="the number to convert",
    )
    parser.add_argument(
        "--from",
        help="the unit of the number",
        metavar="UNIT",
    )
    parser.add_argument(
        "--to",
        help="the unit to convert to",
        metavar="UNIT",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list the supported units and exit",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return its exit code.

    Wrong usage (missing arguments, unknown options) makes argparse print a
    message and exit with code 2.
    """
    parser = build_parser()
    args = vars(parser.parse_args(argv))

    # If the -h or --help option is used, the code below won't execute.

    given = [args.get("value"), args.get("from"), args.get("to")]

    if args.get("list"):
        # Exclude the use of -l or --list option with the others.
        if any(item is not None for item in given):
            parser.error("-l or --list option must be used alone.")

        # List available units.
        print(_format_unit_list())
        return 0

    if any(item is None for item in given):
        parser.error("expected three arguments: value, from_unit and to_unit.")

    try:
        source = api.parse_quantity(args.get("value"), str(args.get("from")))
        result = api.convert_quantity(source, str(args.get("to")))
    except api.ConverterError as error:
        print(error.message, file=sys.stderr)
        return 1

    print(f"{api.format_quantity(source)} = {api.format_quantity(result)}")
    return 0


def _format_unit_list() -> str:
    lines: list[str] = []
    for category, names in api.list_units().items():
        # Non-breaking spaces keep names like "nautical mile" on one line.
        text = ", ".join(name.replace(" ", "\u00a0") for name in names)
        wrapped = textwrap.fill(
            text,
            width=_LIST_WIDTH,
            initial_indent="  ",
            subsequent_indent="  ",
        )
        lines.append(f"{category.capitalize()}:")
        lines.append(wrapped.replace("\u00a0", " "))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
