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

def reform_party(final_party_output, intermediate_party_output):
    party = Party()
    for detection_file in glob.glob(intermediate_party_output+"/*"):
        party += Party().read(detection_file)
    party.write(final_party_output)


def reform_stream(final_stream_output,intermediate_stream_output ):
    stream = Stream()
    for stream_file in glob.glob(intermediate_stream_output+"/*"):
        stream += read(stream_file)
    stream.split()
    stream.write(final_stream_output, format="MSEED")


def run(analysis_start, analysis_len, template_creation_start, template_creation_len, write_streams, intermediate_party_output, final_party_output, intermediate_stream_output, final_stream_output):
    client = Client("http://service.geonet.org.nz")
    # for template creation
    day_len = 86400
    t2 = template_creation_start + (template_creation_len * day_len)
    catalog = client.get_events(
        starttime=template_creation_start, endtime=t2, minmagnitude=2.5, minlatitude=-37.95936, maxlatitude=-36.84226,
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
    if write_streams is True:
        for day in range(1, analysis_len):
            _party, st = tribe.client_detect(
                client=client, starttime=analysis_start + (day - 1) * day_len, endtime=analysis_start + day * day_len, threshold=9.,
                threshold_type="MAD", trig_int=2.0, plot=False, return_stream=True)
            _party.write(intermediate_party_output+"/Detections_day_{0}".format(day))
            st = st.split()  # Required for writing to miniseed
            st.write(intermediate_stream_output+"/{0}.ms".format(day), format="MSEED")
        reform_party(final_party_output, intermediate_party_output)
        reform_stream(final_stream_output,intermediate_stream_output)

    else:
        for day in range(1, analysis_len):
            _party = tribe.client_detect(
                client=client, starttime=analysis_start + (day - 1) * day_len, endtime=analysis_start + day * day_len, threshold=9.,
                threshold_type="MAD", trig_int=2.0, plot=False, return_stream=False)
            _party.write(intermediate_party_output+"/Detections_day_{0}".format(day))
        reform_party(final_party_output, intermediate_party_output)






analysis_start = UTCDateTime(2019, 11, 9)
analysis_len = 3
template_creation_start = UTCDateTime(2019, 11, 9)
template_creation_len = 3
write_streams = True
intermediate_party_output = "test_partys"
final_party_output = "test_party.tgz"
intermediate_stream_output = "test_streams"
final_stream_output = "test_stream"

run(analysis_start, analysis_len, template_creation_start, template_creation_len, write_streams,intermediate_party_output,final_party_output,intermediate_stream_output,final_stream_output)
print('done')
