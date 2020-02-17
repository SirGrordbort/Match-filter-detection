"""
plots waveforms and their picks.

:author: Toby Messerli
:date: 17/2/2020
"""
from obspy import read_events
from obspy.clients.fdsn import Client
from matplotlib import pyplot as plt
import plot_event

client = Client("http://service.geonet.org.nz")
catalog = read_events("repicked_catalog")
for event in catalog.events:
    try:
        fig = plot_event.plot_event_from_client(event, client,length=100)
    except IndexError:
        continue
        # find some way to show the figure without it crashing on the next iteration
