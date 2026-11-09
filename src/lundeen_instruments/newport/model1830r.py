"""Newport 1830-R optical power meter.

Independent implementation of documented remote commands, not copied from
CERCuO/Python. Software-tested only; hardware validation is pending.

Reference: Newport 1830-R Series User's Manual, remote command section.
See docs/supported_devices.md for transport and validation limitations.
"""

from __future__ import annotations

import math
from numbers import Integral
from typing import Any


class Newport1830R:
    """Minimal driver for an 1830-R or 1830-R-GPIB meter.

    Parameters
    ----------
    resource_name:
        VISA resource name, e.g. ``"GPIB0::4::INSTR"`` or a verified USB
        VISA resource identifier. Required unless ``connection`` is supplied.
    connection:
        Optional existing VISA-like resource exposing ``query`` and ``write``.
        Useful for testing or a transport obtained elsewhere. Ownership stays
        with the caller; closing this driver does not close injected resources.
    resource_manager:
        Optional PyVISA-compatible resource manager. Ownership stays with
        the caller.
    backend:
        Optional VISA backend string, e.g. ``"@py"``. Cannot be used with
        ``resource_manager``. When omitted, PyVISA chooses its default.
    timeout_ms:
        Communication timeout in milliseconds for a resource opened here.

    Notes
    -----
    USB on this Newport model may require a manufacturer-specific driver and
    transport; a physical USB connector does not guarantee VISA compatibility.
    """

    def __init__(
        self,
        resource_name: str | None = None,
        *,
        connection: Any | None = None,
        resource_manager: Any | None = None,
        backend: str | None = None,
        timeout_ms: int = 5000,
    ) -> None:
        if connection is not None and resource_name is not None:
            raise ValueError("Supply either resource_name or connection, not both.")
        if connection is None and not resource_name:
            raise ValueError("A VISA resource_name or an existing connection is required.")
        if resource_manager is not None and backend is not None:
            raise ValueError("Pass a resource_manager or backend, not both.")
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive.")

        self._owns_resource = connection is None
        self._owns_manager = False
        self._manager = resource_manager
        self._closed = False

        if connection is None:
            try:
                import pyvisa
            except ImportError as exc:
                raise ImportError(
                    "PyVISA is required to open instruments. "
                    "Install with: pip install 'lundeenlab-instruments[newport]'"
                ) from exc
            if self._manager is None:
                self._manager = pyvisa.ResourceManager(backend) if backend else pyvisa.ResourceManager()
                self._owns_manager = True
            try:
                connection = self._manager.open_resource(resource_name)
            except BaseException:
                if self._owns_manager:
                    self._manager.close()
                raise
            connection.timeout = timeout_ms
            connection.write_termination = "\n"
            connection.read_termination = "\n"
        self._resource = connection

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("This Newport1830R driver has been closed.")

    def query(self, command: str) -> str:
        """Send one query and return the response as stripped text."""
        self._require_open()
        return str(self._resource.query(command)).strip()

    def write(self, command: str) -> None:
        """Send a single command (one per transaction)."""
        self._require_open()
        self._resource.write(command)

    def get_wavelength_nm(self) -> int:
        """Return the current photodetector calibration wavelength (nm)."""
        return int(self.query("W?"))

    def set_wavelength_nm(self, wavelength_nm: int) -> None:
        """Set calibration wavelength (integer nm; detector-specific limits apply)."""
        if isinstance(wavelength_nm, bool) or not isinstance(wavelength_nm, Integral):
            raise TypeError("1830-R wavelength must be an integer number of nm.")
        if not 0 < wavelength_nm < 10000:
            raise ValueError("Wavelength must be a positive integer below 10000 nm.")
        self.write(f"W{wavelength_nm}")

    def set_units_watts(self) -> None:
        """Configure the instrument to return power in watts (U1)."""
        self.write("U1")

    def get_units(self) -> str:
        """Return one of 'W', 'dB', 'dBm', or 'REL'."""
        mapping = {"1": "W", "2": "dB", "3": "dBm", "4": "REL"}
        reply = self.query("U?")
        if reply not in mapping:
            raise ValueError(f"Unknown 1830-R power units response: {reply!r}")
        return mapping[reply]

    def read_power_w(self) -> float:
        """Read numeric optical power in W, refusing ambiguous unit settings.

        Call :meth:`set_units_watts` first if the meter is in dBm/dB/REL mode.
        """
        if self.get_units() != "W":
            raise RuntimeError("Meter is not set to watts. Call set_units_watts() first.")
        result = float(self.query("D?"))
        if not math.isfinite(result):
            raise ValueError("Meter returned non-finite power.")
        return result

    def get_attenuator_enabled(self) -> bool:
        """Read the meter's optical attenuator setting."""
        reply = self.query("A?")
        if reply not in {"0", "1"}:
            raise ValueError(f"Unexpected attenuator response: {reply!r}")
        return reply == "1"

    def set_attenuator_enabled(self, enabled: bool) -> None:
        """Enable or disable the optical attenuator setting."""
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")
        self.write("A1" if enabled else "A0")

    def close(self) -> None:
        """Release only resources owned by this driver."""
        if self._closed:
            return
        self._closed = True
        try:
            if self._owns_resource:
                self._resource.close()
        finally:
            if self._owns_manager and self._manager is not None:
                self._manager.close()

    def __enter__(self) -> Newport1830R:
        self._require_open()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()
