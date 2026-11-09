"""Driver unit tests with simulated command replies (no hardware)."""

import math

import pytest

from lundeen_instruments import Newport1830R


class FakeConnection:
    def __init__(self, *, wavelength="1550", units="1", power="1.234E-03", attenuator="0"):
        self.responses = {"W?": wavelength, "U?": units, "D?": power, "A?": attenuator}
        self.commands = []
        self.closed = False

    def write(self, command):
        self.commands.append(("write", command))
        if command == "U1":
            self.responses["U?"] = "1"
        if command.startswith("W") and command != "W?":
            self.responses["W?"] = command[1:]
        if command in {"A0", "A1"}:
            self.responses["A?"] = command[-1]

    def query(self, command):
        self.commands.append(("query", command))
        return self.responses[command]

    def close(self):
        self.closed = True


class FakeManager:
    def __init__(self):
        self.conn = FakeConnection()
        self.closed = False
        self.address = None

    def open_resource(self, address):
        self.address = address
        return self.conn

    def close(self):
        self.closed = True


def test_power_and_units():
    transport = FakeConnection(units="3")
    with Newport1830R(connection=transport) as meter:
        with pytest.raises(RuntimeError, match="watts"):
            meter.read_power_w()
        meter.set_units_watts()
        assert meter.get_units() == "W"
        assert math.isclose(meter.read_power_w(), 0.001234)
    assert transport.commands[-2:] == [("query", "U?"), ("query", "D?")]
    assert not transport.closed  # injected connection remains caller-owned


def test_wavelength_and_attenuator():
    transport = FakeConnection()
    meter = Newport1830R(connection=transport)
    meter.set_wavelength_nm(1549)
    assert meter.get_wavelength_nm() == 1549
    meter.set_attenuator_enabled(True)
    assert meter.get_attenuator_enabled()
    meter.set_attenuator_enabled(False)
    assert not meter.get_attenuator_enabled()
    with pytest.raises(TypeError):
        meter.set_wavelength_nm(1549.5)
    with pytest.raises(TypeError):
        meter.set_wavelength_nm(True)
    with pytest.raises(ValueError):
        meter.set_wavelength_nm(-1)
    with pytest.raises(TypeError):
        meter.set_attenuator_enabled(1)


def test_bogus_units_and_values():
    with Newport1830R(connection=FakeConnection(units="bad")) as meter:
        with pytest.raises(ValueError, match="Unknown"):
            meter.get_units()
    with Newport1830R(connection=FakeConnection(power="NaN")) as meter:
        with pytest.raises(ValueError, match="non-finite"):
            meter.read_power_w()
    with Newport1830R(connection=FakeConnection(attenuator="unknown")) as meter:
        with pytest.raises(ValueError, match="attenuator"):
            meter.get_attenuator_enabled()


def test_connection_ownership_and_closed_state(monkeypatch):
    mgr = FakeManager()
    import sys
    import types
    fake_pyvisa = types.SimpleNamespace(ResourceManager=lambda *args: mgr)
    monkeypatch.setitem(sys.modules, "pyvisa", fake_pyvisa)
    meter = Newport1830R("GPIB0::4::INSTR", timeout_ms=1000)
    assert mgr.address == "GPIB0::4::INSTR"
    assert mgr.conn.write_termination == "\n"
    assert mgr.conn.read_termination == "\n"
    assert mgr.conn.timeout == 1000
    meter.close()
    meter.close()
    assert mgr.conn.closed and mgr.closed
    with pytest.raises(RuntimeError, match="closed"):
        meter.query("W?")


def test_supplied_manager_owned_by_caller(monkeypatch):
    mgr = FakeManager()
    import sys
    import types
    monkeypatch.setitem(sys.modules, "pyvisa", types.SimpleNamespace(ResourceManager=lambda *args: mgr))
    with Newport1830R("GPIB0::4::INSTR", resource_manager=mgr) as meter:
        assert meter.get_wavelength_nm() == 1550
    assert mgr.conn.closed
    assert not mgr.closed


def test_validation():
    with pytest.raises(ValueError, match="resource_name"):
        Newport1830R()
    with pytest.raises(ValueError, match="either"):
        Newport1830R("ADDR", connection=FakeConnection())
    with pytest.raises(ValueError, match="positive"):
        Newport1830R(connection=FakeConnection(), timeout_ms=0)
    with pytest.raises(ValueError, match="manager or backend"):
        Newport1830R("ADDR", resource_manager=FakeManager(), backend="@py")
