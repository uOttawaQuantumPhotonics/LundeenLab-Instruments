# CERCuO → LundeenLab migration

The original source is kept separate from new drivers to avoid changing known working implementations during migration.

## One-time import procedure

1. Confirm permission to reuse and redistribute the existing source. CERCuO/Python currently has no repository-wide license file.
2. From the lab package root, run one of:

```bash
python scripts/import_cercuo.py --source PATH_TO_CERCuO_Python
# or
python scripts/import_cercuo.py --download --ref main
```

3. Inspect `src/lundeen_instruments/legacy/Core/` and `src/lundeen_instruments/legacy/CERCUO_MANIFEST.json`. The manifest records the exact SHA-256 of each original Python source file.
4. Commit the imported files to **your own** lab repository (not to CERCuO), after rights review, and open a PR.
5. Test the original routines on the actual lab hardware and record what was tested. The importer does not modify the original code and cannot fix missing CERCuO dependencies automatically.
6. After merging, every lab member can install directly with pip from the lab GitHub repository. The importer is **not** a step students need to repeat.

The importer copies **all Python source code under `Core/`** (Drivers, Dependencies, GUIs, Methods, and any Python files in Documentation). It excludes CSV/TXT experiment data and large PDF manuals; obtain the original vendor documents separately.

## Working with preserved drivers

Install any device-specific upstream Python dependencies first. Some legacy scripts use `sys.path` and old absolute imports, so explicitly activate compatibility mode:

```python
from lundeen_instruments.legacy import enable_legacy_imports
enable_legacy_imports()

from KDC101 import KDC101  # preserved CERCuO implementation
```

This compatibility hook makes the historical `Dependencies/` and `Drivers/` directories importable, but it does not rewrite any legacy source, silently instantiate instruments, or imply that all imported code is importable in every operating system. Some original scripts depend on missing modules such as `globalsFile` or `__santecTSL1__`. Resolve and test these separately, without modifying the original archive.

## New and old APIs remain separate

- New code: `from lundeen_instruments import Newport1830R` (namespaced, tested unit-level driver).
- Old code: `enable_legacy_imports(); from Newport1830R import Newport1830R` (legacy API and requirements retained).

Prefer a new adapter module for any modernized driver to avoid breaking the historic scripts. Clearly distinguish hardware-validated, software-tested, and archived-only drivers.
