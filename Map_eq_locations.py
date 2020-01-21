# for mapping events from the obspy catalog file into arcGIS
from obspy import read_events

catalog = read_events("catalog")
for event in catalog:
    print(event.Origin)