"""Module to type check implementation classes against protocols."""

from instrument_lib.instruments import (
    KS_E36100_PS,
    KS_E36300_PS,
    RS_NGPx,
    ETS_Positioner,
    RS_Positioner,
)
from instrument_lib.instruments.power_supplies.power_supply import is_power_supply_type
from instrument_lib.instruments.positioners.positioner import is_positioner_type


e36102b_ps = KS_E36100_PS()
e36312a_ps = KS_E36300_PS()
rs_ngp800_ps = RS_NGPx()

is_power_supply_type(e36102b_ps)
is_power_supply_type(e36312a_ps)
is_power_supply_type(rs_ngp800_ps)


ets_positioner = ETS_Positioner()
rs_positioner = RS_Positioner()

is_positioner_type(ets_positioner)
is_positioner_type(rs_positioner)
