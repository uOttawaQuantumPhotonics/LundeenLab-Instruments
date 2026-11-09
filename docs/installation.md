# Installation

Requires Python 3.10 or newer. Virtual environments are recommended.

## Install from a local folder

After extracting the downloaded lab source ZIP, open a terminal in the folder containing `pyproject.toml`:

```bash
python -m pip install ".[newport]"
```

To install all development/test dependencies:

```bash
python -m pip install -e ".[newport,dev]"
python -m pytest -q
```

## Install from GitHub (after the package is committed to `main`)

```bash
python -m pip install "lundeenlab-instruments[newport] @ git+https://github.com/uOttawaQuantumPhotonics/LundeenLab-Instruments.git"
```

The build uses standard `pyproject.toml` packaging and does not require custom `sys.path` edits for **new** drivers. Historic CERCuO drivers are opt-in through `enable_legacy_imports()` and only present after maintainers commit them (see [migration](migration.md)).

## Optional instrument dependencies

```bash
# Newport and other PyVISA-connected instruments
python -m pip install ".[newport]"

# Optional pure Python VISA backend, supported hardware permitting
python -m pip install ".[visa-py]"

# Development tooling
python -m pip install ".[dev]"

# Common scientific dependencies used by some archived CERCuO drivers
python -m pip install ".[legacy]"
```

The `legacy` extra does not include proprietary vendor SDKs, so specific legacy instruments may require additional software. Do not assume a direct Newport USB connection is VISA-compatible; the required backend/API depends on the instrument variant.

## Tools

```bash
lundeen-instruments list
lundeen-instruments list --backend @py
```

## Publication to PyPI

`pip install lundeenlab-instruments` (without Git URL) will only work if/when the lab registers and publishes the distribution on PyPI. No PyPI package has been published as part of this delivery. Select a license and confirm redistributed source rights before public releases.
