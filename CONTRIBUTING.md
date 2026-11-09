# Contributing to LundeenLab-Instruments

## Development workflow

1. Branch from `main` (e.g. `feature/newport-driver`).
2. Install `python -m pip install -e ".[newport,dev]"`.
3. Add a minimal working example in `examples/` and simulation tests in `tests/`.
4. Run `python -m pytest -q` and `python -m build --wheel`.
5. Open a pull request. Do not merge a device's “hardware-validated” status without an actual hardware test record.

## Driver conventions

- Modules live in `src/lundeen_instruments/<manufacturer>/`.
- Prefer standard Python snake_case methods and return numeric quantities in documented units.
- Open connections lazily, handle timeouts, and close owned resources safely.
- Avoid import-time hardware initialization, personal machine paths, raw measurement data, passwords and vendor binaries.
- Depend on `pylablib`, `PyMeasure` or vendor libraries whenever they already provide robust drivers.
- Use a mock/fake transport in unit tests and record actual instrument model, firmware, interface, OS, and tester for hardware checks.

## Historic CERCuO code

Do **not** rename methods, auto-format, or silently fix the archived `legacy/Core` drivers during the first migration. Changes can be tracked later in separate adapters, with legacy source retained for traceability. Confirm provenance and redistribution rights first; note that public GitHub access does not, by itself, grant a software license.
