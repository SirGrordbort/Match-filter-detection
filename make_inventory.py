from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy import read_events

client = Client("GEONET")
starttime = UTCDateTime(2018, 12, 9)
endtime = UTCDateTime(2020, 1, 9)
minlatitude = -37.95936
maxlatitude = -36.84226
minlongitude = 176.63818
maxlongitude = 177.80548
level = "channel"
# stations = set(())
catalog = read_events("repicked_catalog")

seed_ids = {p.waveform_id.get_seed_string().split('.') for ev in catalog for p in ev.picks}
bulk = [(sid[0], sid[1], sid[2], sid[3], starttime, endtime) for sid in seed_ids]
inventory = client.get_waveforms_bulk(bulk, level=level)

# for event in catalog.events:
#     for pick in event.picks:
#         wav_id = pick.waveform_id
#         stations.add(wav_id.station_code)
# station_str = ""
# for station in stations:
#     station_str += str(station)
#     station_str += ","
# station_str = station_str[:-1]
# inventory = client.get_stations(starttime=starttime, endtime=endtime, level=level, station=station_str)
inventory.write("inventory.xml", "STATIONXML")
