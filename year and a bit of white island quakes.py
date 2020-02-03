

import logging
    
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")

from obspy import UTCDateTime
from collections import Counter
from obspy.clients.fdsn import Client
from eqcorrscan.utils.catalog_utils import filter_picks
from eqcorrscan import Tribe
import glob
from eqcorrscan import Party
client = Client("http://service.geonet.org.nz")
# -this gives no data but i can see eqs do exist for the given parameters in the geonet system?
# -is this how eqcorrscan is meant to be used i.e long time period many templates?

# for analysis
detection_t1 = UTCDateTime(2018, 12, 9)
detection_num_days = 396

#for template creation
num_days = 30
day_len = 86400
t1 = UTCDateTime(2019, 11, 9)
t2 = t1 + (num_days * day_len)
catalog = client.get_events(
    starttime=t1, endtime=t2, minmagnitude=2.4, minlatitude=-37.95936, maxlatitude=-36.84226,
    minlongitude=176.63818, maxlongitude=177.80548)
fig = catalog.plot(projection="local", resolution="h")
# Get rid of duplicately picked arrivals.
for event in catalog:
    counted_stations = Counter(p.waveform_id.get_seed_string() for p in event.picks)
    _picks = []
    for seed_id, n_picks in counted_stations.items():
        nslc_picks = [p for p in event.picks if p.waveform_id.get_seed_string() == seed_id]
        if n_picks == 1:
            _picks.append(nslc_picks[0])
        else:
            print("Multiple picks for {0}".format(seed_id))
            nslc_picks.sort(key=lambda p: p.time)
            _picks.append(nslc_picks[0])
    event.picks = _picks
    
catalog = filter_picks(catalog=catalog, evaluation_mode="manual", top_n_picks=20)



tribe = Tribe().construct(
    method="from_client", lowcut=2.0, highcut=15.0, samp_rate=50.0, length=6.0,
    filt_order=4, prepick=0.5, client_id=client, catalog=catalog, data_pad=20.,
    process_len=day_len, min_snr=5.0, parallel=True)
print(tribe)
print(tribe[0])
fig = tribe[0].st.plot(equal_scale=False, size=(800, 600))

tribe.templates = [t for t in tribe if len({tr.stats.station for tr in t.st}) >= 5]
print(tribe)


for day in range(1, detection_num_days):
    _party, st = tribe.client_detect(
        client=client, starttime=detection_t1+(day-1)*day_len, endtime=detection_t1+day*day_len, threshold=9.,
        threshold_type="MAD", trig_int=2.0, plot=False, return_stream=False)
    _party.write("year_dets_month_temps/Year_Detections/Detections_day_{0}".format(day))


party = Party()
for detection_file in glob.glob("year_dets_month_temps/Year_Detections/*"):
    party += Party().read(detection_file)
fig = party.plot(plot_grouped=True)
print('done')

"""
catalog2 = client.get_stations(starttime = UTCDateTime(2019, 11, 19, 3, 22, 45, 26327), endtime = UTCDateTime(2019, 11, 19, 3, 22, 59, 269999) ,station = "OPRZ", channel = "HHN")

for day in range(1, detection_num_days):
    _party = tribe.client_detect(
        client=client, starttime=detection_t1+(day-1)*day_len, endtime=detection_t1+day*day_len, threshold=9.,
        threshold_type="MAD", trig_int=2.0, plot=False, return_stream=False)
    _party.write("year_dets_month_temps/test_saves/Detections_day_{0}".format(day))

print(catalog2)
Inventory created at 2020-01-16T19:48:14.000000Z
        Created by: Delta
                    
        Sending institution: GeoNet (WEL(GNS_Test))
        Contains:
                Networks (1):
                        NZ
                Stations (1):
                        NZ.OPRZ (Ohinepanea)
                Channels (0):
"""