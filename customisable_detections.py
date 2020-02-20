"""
Creates a party and associated stream for each day in the specified range

:author: Toby Messerli, Calum J Chamberlain
:date: 13/2/2020
"""
# FIXME changes without testing
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")

from obspy import UTCDateTime
from collections import Counter
from obspy.clients.fdsn import Client
from eqcorrscan.utils.catalog_utils import filter_picks
from eqcorrscan import Tribe
import numpy as np


def run(analysis_start, analysis_len, template_creation_start, template_creation_len, write_streams, party_output_folder, stream_output_folder, min_mag):
    """
            begins by creating an tribe of templates from the given specifications then runs these templates against a
            specified length of seismometer data.

                :type analysis_start: UTCDateTime
                :param analysis_start: the start time for data that the templates
                will be run against
                :type analysis_len: int :param analysis_len: the length of time (days) to run the
                templates against
                :type template_creation_start: UTCDateTime
                :param template_creation_start: the
                start time for the data used in template creation :type template_creation_len: int
                :param
                template_creation_len: length of data (days) used to look for suitable templates
                :type write_streams:
                bool
                :param write_streams: whether this function should save the streams used when detecting events
                :type party_output_folder, stream_output_folder: string :param party_output_folder,
                stream_output_folder: the folder name for where to save the stream and party file outputs :type
                min_mag: double :param min_mag: the minimum magnitude for an event that a template can be based on
    """

    client = Client("http://service.geonet.org.nz")
    day_len = 86400
    template_creation_end_time = template_creation_start + (template_creation_len * day_len)

    # makes a collection of events to make templates from
    catalog = client.get_events(
        starttime=template_creation_start, endtime=template_creation_end_time, minmagnitude=min_mag, minlatitude=-37.95936, maxlatitude=-36.84226,
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

    # selects only the 20 most picked stations
    catalog = filter_picks(catalog=catalog, evaluation_mode="manual", top_n_picks=20)

    # creates and stores group of template objects
    tribe = Tribe().construct(
        method="from_client", lowcut=2.0, highcut=15.0, samp_rate=50.0, length=6.0,
        filt_order=4, prepick=0.5, client_id=client, catalog=catalog, data_pad=20.,
        process_len=day_len, min_snr=5.0, parallel=False)
    print(tribe)
    print(tribe[0])

    # keeps only those templates which have more than 5 associated channels
    tribe.templates = [t for t in tribe if len({tr.stats.station for tr in t.st}) >= 5]
    print(tribe)

    if write_streams is True:
        for day in range(1, analysis_len):
            _party, st = tribe.client_detect(
                client=client, starttime=analysis_start + (day - 1) * day_len, endtime=analysis_start + day * day_len, threshold=9.,
                threshold_type="MAD", trig_int=2.0, plot=False, return_stream=True)
            _party.write(party_output_folder + "/Detections_day_{0}".format(day))
            for trace in st:
                trace.data = trace.data.astype(np.int32)
            st = st.split()  # Required for writing to miniseed
            st.write(stream_output_folder + "/{0}.ms".format(day), format="MSEED")

    else:
        for day in range(1, analysis_len):
            _party = tribe.client_detect(
                client=client, starttime=analysis_start + (day - 1) * day_len, endtime=analysis_start + day * day_len, threshold=9.,
                threshold_type="MAD", trig_int=2.0, plot=False, return_stream=False)
            _party.write(party_output_folder + "/Detections_day_{0}".format(day))

if __name__ == "__main__":
    analysis_start = UTCDateTime(2018, 12, 9)  # the start time for finding detections
    analysis_len = 396  # how long (days) after the start time the program should look for detections
    template_creation_start = UTCDateTime(2018, 12, 9) # start time for finding templates
    template_creation_len = 396  # how long (days) after the start time the program should look for templates
    write_streams = True  # whether the program should save the stream as well as the party

    # where the program should save the streams and parties for each day
    intermediate_party_output = "partys"
    intermediate_stream_output = "streams"

    min_mag = 3.5  # the minimum magnitude a template event can be

    # actually runs the program with the specified input parameters
    run(analysis_start, analysis_len, template_creation_start, template_creation_len, write_streams, intermediate_party_output, intermediate_stream_output, min_mag)
    print('done')
