"""Read an 1830-R optical power meter (physical hardware required).

Install: pip install '.[newport]'
Find address: lundeen-instruments list
"""

from lundeen_instruments import Newport1830R

RESOURCE = "GPIB0::4::INSTR"  # Replace with your actual VISA resource

with Newport1830R(RESOURCE) as meter:
    meter.set_wavelength_nm(1550)
    meter.set_units_watts()
    print(f"Calibration wavelength: {meter.get_wavelength_nm()} nm")
    print(f"Power: {meter.read_power_w():.6g} W")
