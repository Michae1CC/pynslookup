from __future__ import annotations

import argparse
import sys

from collections.abc import Sequence

from typing import cast

from .const import PROGRAM_NAME

from ._dns import RecordType


def _run(args: argparse.Namespace) -> int:

    # TODO: This can be a list of record types
    record_type: RecordType = RecordType((cast(str, args._type)).upper())
    port: int = args.port
    recurse: bool = args.recurse

    print(record_type)
    print(port)
    print(recurse)

    return 0


def main(argv: Sequence[str] | None = None) -> int:

    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME)

    parser.add_argument(
        "-type",
        type=str,
        help=(f"Changes the resource record type for the query."),
        default=f"A",
        metavar="type",
        dest="_type",
    )

    parser.add_argument(
        "-port",
        type=int,
        help=(
            f"Changes the default TCP/UDP DNS name server port to the value specified."
        ),
        default=50,
        metavar="port",
        dest="port",
    )

    parser.add_argument(
        "-recurse",
        type=bool,
        help=(
            f"Tells the DNS name server to query other servers if it doesn't have the information."
        ),
        default=False,
        metavar="recurse",
        dest="recurse",
    )

    args = parser.parse_args()

    return _run(args)
