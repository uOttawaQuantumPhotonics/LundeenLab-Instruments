# LundeenLab-Instruments

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Unit tests](https://github.com/uOttawaQuantumPhotonics/LundeenLab-Instruments/actions/workflows/tests.yml/badge.svg)](https://github.com/uOttawaQuantumPhotonics/LundeenLab-Instruments/actions/workflows/tests.yml)
[![Package version](https://img.shields.io/badge/version-0.1.0a0-6F42C1)](pyproject.toml)
[![pip installable](https://img.shields.io/badge/install-pip-0A9EDC?logo=pypi&logoColor=white)](docs/installation.md)
[![Development status](https://img.shields.io/badge/status-pre--release-F59E0B)](docs/supported_devices.md)
[![License pending](https://img.shields.io/badge/license-pending-lightgrey)](docs/provenance.md)

**An installable Python toolkit for scientific instruments used by the Lundeen Lab, University of Ottawa.**

The project complements [pylablib](https://www.pylablib.io/), [PyMeasure](https://pymeasure.readthedocs.io/), and vendor SDKs rather than duplicating maintained drivers. It also provides a **lossless import path** for preserving the existing [CERCuO/Python](https://github.com/CERCuO/Python) source code inside a structured package, subject to the lab's reuse authorization.

> **Status:** This source archive contains the tested packaging foundation and a newly written Newport 1830-R driver. The complete CERCuO source is **not included in the archive**. Run the one-time importer described below to bring the original files into `legacy/Core/` unchanged. Existing hardware behavior is not represented as validated by this new packaging layer.

## Install with pip

After the project files are committed to `main`:

```bash
python -m pip install "lundeenlab-instruments[newport] @ git+https://github.com/uOttawaQuantumPhotonics/LundeenLab-Instruments.git"
```

Install from a downloaded/extracted source directory:

```bash
python -m pip install ".[newport]"
```

For development:

```bash
python -m pip install -e ".[newport,dev]"
python -m pytest -q
```

**Note:** `pip install lundeenlab-instruments` without a GitHub URL will only work **after** this name is published to PyPI. The repository can be pip-installed directly without PyPI.

## Minimal example

```python
from lundeen_instruments import Newport1830R

# Use your instrument's *verified* VISA resource name.
with Newport1830R("GPIB0::4::INSTR") as meter:
    meter.set_wavelength_nm(1550)
    meter.set_units_watts()
    print(f"{meter.read_power_w():.6g} W")
```

Find reachable VISA resources:

```bash
lundeen-instruments list
```

The standalone Newport example is software-tested, not yet verified against a specific physical USB interface.

## One-time CERCuO migration (for maintainers)

Use the importer to copy **all Python source files** from CERCuO into the separately contained legacy area **without rewriting the originals**:

```bash
# From a local checkout of the CERCuO/Python repo
python scripts/import_cercuo.py --source "../Python"

# OR download CERCuO/Python from GitHub on a machine with internet access
python scripts/import_cercuo.py --download
```

Inspect changes, obtain any needed reuse permissions, then **commit the imported files** to this lab repository. After that, lab members only need `pip install ...` from GitHub; **they do not need to run the importer**.

Historic drivers can be accessed with explicit legacy compatibility mode, e.g.:

```python
from lundeen_instruments.legacy import enable_legacy_imports
enable_legacy_imports()
from Newport1830R import Newport1830R  # original CERCuO class
```

Legacy imports may require additional vendor libraries and on-computer configuration. Their original source is intentionally preserved; this opt-in mode adds legacy paths only when requested. For new code, prefer the modern namespaced driver API.

See [CERCuO migration](docs/migration.md), [supported instruments](docs/supported_devices.md), [installation](docs/installation.md), and [provenance and license](docs/provenance.md).

## Scope and principles

- **Small default install**; dependencies for specific devices are optional.
- **Reproducible unit tests** using simulated instruments, plus hardware verification records when available.
- **No hard-coded personal paths in new drivers** and no measurement data mixed into the installable library.
- **Preserve original CERCuO code and author credits**, while modernized implementations live in the normal `lundeen_instruments` modules.
- **Use existing vendor/third-party APIs where suitable**, instead of maintaining unnecessary duplicate code.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). This repository's current release is pre-alpha and has **not yet been assigned an open-source license**. The lab must confirm rights for any imported legacy code before redistribution or public release.
