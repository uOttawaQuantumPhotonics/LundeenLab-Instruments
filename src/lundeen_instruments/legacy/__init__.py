"""Opt-in compatibility for unmodified CERCuO laboratory scripts.

The legacy files are imported by maintainers using scripts/import_cercuo.py.
They are not imported automatically: some require specific third-party drivers,
Windows configuration, or supporting code that is absent in CERCuO/Python.
"""

from __future__ import annotations

from pathlib import Path
import sys


def enable_legacy_imports() -> list[str]:
    """Make *bundled* legacy Dependencies and Drivers available as old top-level modules.

    Preserves old absolute imports such as `from __connection__ import Connection`.
    The caller opts in explicitly; this can expose top-level module names.

    Returns
    -------
    list[str]
        Paths added to sys.path (in precedence order).

    Raises
    ------
    FileNotFoundError
        The CERCuO files have not yet been imported into this package.
    """
    root = Path(__file__).resolve().parent / "Core"
    dependencies = root / "Dependencies"
    drivers = root / "Drivers"
    if not (dependencies.is_dir() and drivers.is_dir()):
        raise FileNotFoundError(
            "CERCuO legacy files are not bundled. The package maintainer must "
            "run `python scripts/import_cercuo.py --download`, commit the files, "
            "then reinstall the package."
        )
    added = []
    # Reversed insertion yields the intended final order: Dependencies, Drivers.
    for path in (drivers, dependencies):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
            added.append(path_text)
    return list(reversed(added))
