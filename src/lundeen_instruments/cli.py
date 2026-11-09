"""Command-line resource discovery helper."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lundeen-instruments", description="Lundeen Lab instrument utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="list VISA resources detectable by PyVISA")
    list_parser.add_argument("--backend", default=None, help="optional VISA backend such as @py")
    args = parser.parse_args(argv)

    if args.command == "list":
        try:
            import pyvisa
        except ImportError:
            parser.exit(2, "PyVISA is not installed. Install: pip install 'lundeenlab-instruments[newport]'\n")
        manager = pyvisa.ResourceManager(args.backend) if args.backend else pyvisa.ResourceManager()
        try:
            resources = manager.list_resources()
            if not resources:
                print("No VISA resources found. Confirm interface drivers and backend.")
            else:
                for resource in resources:
                    print(resource)
        finally:
            manager.close()
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
