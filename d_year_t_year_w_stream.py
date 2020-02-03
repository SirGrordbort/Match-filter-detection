# for making a party from a year of templates and data including the streams
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
from obspy import Stream
from obspy import read

client = Client("http://service.geonet.org.nz")
# -this gives no data but i can see eqs do exist for the given parameters in the geonet system?
# -is this how eqcorrscan is meant to be used i.e long time period many templates?

# for analysis
detection_t1 = UTCDateTime(2018, 11, 9)
detection_num_days = 396

# for template creation
num_days = 396
day_len = 86400
t1 = UTCDateTime(2018, 11, 9)
t2 = t1 + (num_days * day_len)
catalog = client.get_events(
    starttime=t1, endtime=t2, minmagnitude=3.5, minlatitude=-37.95936, maxlatitude=-36.84226,
    minlongitude=176.63818, maxlongitude=177.80548)

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
    process_len=day_len, min_snr=5.0, parallel=False)
print(tribe)
print(tribe[0])

tribe.templates = [t for t in tribe if len({tr.stats.station for tr in t.st}) >= 5]
print(tribe)

for day in range(1, detection_num_days):
    _party, st = tribe.client_detect(
        client=client, starttime=detection_t1 + (day - 1) * day_len, endtime=detection_t1 + day * day_len, threshold=9.,
        threshold_type="MAD", trig_int=2.0, plot=False, return_stream=True)
    _party.write("year_with_stream/Detections_day_{0}".format(day))
    st = st.split()  # Required for writing to miniseed
    st.write("y_d_y_t_w_s/{0}.ms".format(day), format="MSEED")

party = Party()
for detection_file in glob.glob("year_with_stream/*"):
    party += Party().read(detection_file)

stream = Stream()
for stream_file in glob.glob("y_d_y_t_w_s/*"):
    stream += read(stream_file)
stream.split()
stream.write("year_streams", format = "MSEED")
party.write("year_party")
print('done')
