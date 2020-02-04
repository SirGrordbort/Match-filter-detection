from eqcorrscan import Party
from obspy import read_events
stream = read_events("stream.ms")
party = Party().read("party.tgz")
repicked_catalog = party.lag_calc(stream, pre_processed=False, shift_len=0.5, min_cc=0.4)
repicked_catalog.write("repicked_catalog", "QUAKEML")
