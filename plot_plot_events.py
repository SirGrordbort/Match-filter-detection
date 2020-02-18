import make_plot_events
import multi_picks_on_stream

"""


:author: Toby Messerli
:date: 17/2/2020
"""
from obspy import read_events
from obspy.clients.fdsn import Client
from eqcorrscan import Party

client = Client("http://service.geonet.org.nz")
catalog = read_events("repicked_catalog")
party = Party().read("party_with_origins.tgz")
before_events = []
print("making before events")
for fam in party.families:
    before_events.extend([detection.event for detection in fam.detections])
print("making plot events")
plot_events = make_plot_events.make_plot_events(catalog.events, before_events)
print("making plots")
for plot_event in plot_events:
    if plot_event.all_picks is not None:
        multi_picks_on_stream.plot_event_from_client(plot_event, client, length=100)
