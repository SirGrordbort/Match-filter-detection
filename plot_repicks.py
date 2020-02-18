"""
saves waveforms and their picks after they have been repicked.

:author: Toby Messerli
:date: 17/2/2020
"""
from obspy import read_events
from obspy.clients.fdsn import Client
from save_pick_waveforms import process_events

client = Client("http://service.geonet.org.nz")
catalog = read_events("repicked_catalog")
process_events(catalog.events, client, "repicked_waveforms")