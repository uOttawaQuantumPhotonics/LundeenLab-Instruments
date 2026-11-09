# Supported instruments and validation

| Instrument | API status | Hardware status | Backend |
|---|---|---|---|
| Newport 1830-R / 1830-R-GPIB | Minimal implementation, unit-tested | **Not yet hardware-validated** | PyVISA-compatible connection |

## Newport 1830-R

Commands are independently implemented against the [manufacturer's user manual](https://www.newport.com/medias/sys_master/images/images/h5c/hb2/8796988604446/1830-R-Manual-RevA.pdf):

- `W?` and `Wnnnn`: calibration wavelength, integer nm
- `U1`, `U?`: select/query watts (return units must be checked)
- `D?`: read power in currently selected units
- `A0`, `A1`, `A?`: attenuator setting

The command layer is unit-tested with a simulated transport. We have **not** verified the physical USB, serial, or GPIB connection using the target hardware. The original meter's USB port may require a manufacturer-specific driver/API rather than a PyVISA resource. The manufacturer documents USB line-feed termination; the driver sets `\n` on resources it opens.

**Before first measurement:** Check physical interface and correct resource identifier; compare a series of known power readings against the front panel/reference meter. Verify wavelength calibration, unit changes, attenuator state and safe connection cleanup. Record model, interface, firmware, detector head and test date.

## Contributions

Prefer existing maintained instrument packages when they provide equivalent functionality. New drivers should include an example, unit tests using a fake connection, documentation on physical interfaces, and hardware validation status. Do not include raw experiment data, usernames, credentials, or unpublished vendor SDKs.

## Archived CERCuO implementations (after migration)

The importer includes all upstream Python driver sources in an isolated `legacy/Core/` hierarchy. Their API remains that of CERCuO. The archive is **not** independently validated by this starter package, even if the upstream files are known to work in their original laboratory environment. Check runtime dependencies and specific hardware before use.

See [migration](migration.md) for provenance and installation details.
