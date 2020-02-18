"""
saves waveforms and their picks before they have been repicked.

:author: Toby Messerli
:date: 18/2/2020
"""
from eqcorrscan import Party
from save_pick_waveforms import process_events
from obspy.clients.fdsn import Client

client = Client("http://service.geonet.org.nz")
party = Party().read("party_with_origins.tgz")
for fam in party.families:
    process_events([detection.event for detection in fam.detections], client, "picked_waveforms")