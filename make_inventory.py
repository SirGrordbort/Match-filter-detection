"""
makes an obspy inventory object which holds all of the stations and channels associated with the events in the given
catalog
:author: Toby Messerli, Calum Chamberlain
:date: 13/2/2020
"""

from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy import read_events

client = Client("GEONET")
starttime = UTCDateTime(2018, 12, 9)
endtime = UTCDateTime(2020, 1, 9)
level = "channel"
catalog = read_events("repicked_catalog")

seed_ids = {p.waveform_id.get_seed_string().split('.') for ev in catalog for p in ev.picks}
bulk = [(sid[0], sid[1], sid[2], sid[3], starttime, endtime) for sid in seed_ids]
inventory = client.get_waveforms_bulk(bulk, level=level)
inventory.write("inventory.xml", "STATIONXML")
