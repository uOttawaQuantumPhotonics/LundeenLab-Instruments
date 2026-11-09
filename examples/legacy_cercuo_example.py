"""Import an unchanged CERCuO driver once maintainers have bundled the sources.

Run `python scripts/import_cercuo.py --source ../Python` during package preparation.
Do not run instrument commands without connected/verified hardware.
"""
from lundeen_instruments.legacy import enable_legacy_imports

enable_legacy_imports()
from Newport1830R import Newport1830R  # noqa: E402 - legacy top-level module

# meter = Newport1830R("GPIB0::4::INSTR")
# print(meter.GetWavelength())
