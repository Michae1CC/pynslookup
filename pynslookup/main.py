from __future__ import annotations

import sys

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    print("Hello world")
    print(argv)
    return 0
