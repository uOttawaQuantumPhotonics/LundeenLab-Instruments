"""CLI unit tests without actual VISA hardware."""

import sys
import types

from lundeen_instruments.cli import main


def test_list_resources(capsys, monkeypatch):
    class Manager:
        def list_resources(self):
            return ("GPIB0::4::INSTR",)

        def close(self):
            pass

    monkeypatch.setitem(sys.modules, "pyvisa", types.SimpleNamespace(ResourceManager=lambda *args: Manager()))
    assert main(["list"]) == 0
    assert "GPIB0::4::INSTR" in capsys.readouterr().out
