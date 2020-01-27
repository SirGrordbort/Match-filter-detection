import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")

from obspy import UTCDateTime, Catalog
from collections import Counter
from obspy.clients.fdsn import Client
from eqcorrscan.utils.catalog_utils import filter_picks
from eqcorrscan import Tribe

# -access the geonet database
client = Client("http://service.geonet.org.nz")
t1 = UTCDateTime(2019, 12, 6)
t2 = t1 + 86400
# -if I just keep pushing out the date does this push out the length of time the templates will match against?
detection_endtime = UTCDateTime(2019, 12, 8)

# -Gets specific earthquake events that fit within the given specifications.
# -Each earthquake has a bunch of associated stations and each station has a bunch of channels each channel has a p and s wave pick for the earthquake
# -What is the "WARNING Data for KUZ.HHN is 3.783291666666667 hours long, which is less than 80 percent of the desired length, will not use"?
# Surely each event stored in the catalog is only a few seconds long so having 3 hours of data is still significant
# -"TypeError: The parameter 'includearrivals' is not supported by the service."? this ok without it?
catalog = client.get_events(
    starttime=t1, endtime=t2, minmagnitude=2.5, minlatitude=-38.0, maxlatitude=-37.0,
    minlongitude=177.0, maxlongitude=178.0)

# - plot says it has 4 events but only displays 3?
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
    

# -the catalog holds a bunch of earthquake events which add p and s wave picks to siesmometers, the filter picks selects the 20 stations with the
# greatest total number of all picks so essentially the stations with the most data. 
# - Why?
catalog = filter_picks(catalog=catalog, top_n_picks=20) # evaluation_mode="manual")

# -Makes a group of template objects (Tribe) from the events in the catalog
# -Takes each event in the catalog and makes a template from it if it meets the specifications. each template contains all channels that meet the requirements
# -Highcut is the highest allowed frequency for the template and must be at most half the samp_rate
# -Length is the length of the template waveform in seconds 
# -Prepick is the number of seconds prior to the earthquake wave arrival. needed to compare the wavey bit to the non wavey bit 0.5 seconds is usually good
# -Always set datapad to 20?
# -Each template contains the event but also the data to run the event over
# -Process_len must be set to the same length as what exactly? is the process length the data to run the template against?
# -"WARNING No pick for NZ.KNZ.10.HHN" if there is no pick for this channel does that mean there was a pick on one of the other channels and catalog includes
# all channels for events where there is a pick on at least one channel?
process_len = 86400
tribe = Tribe().construct(
    method="from_client", lowcut=2.0, highcut=15.0, samp_rate=50.0, length=6.0,
    filt_order=4, prepick=0.5, client_id=client, catalog=catalog, data_pad=20.,
    process_len=process_len, min_snr=5.0, parallel=True)
print(tribe)
print(tribe[0])

# -In this plot the first channel has the last part of the waveform cut off. Is this a problem? would increasing length in tribe construction solve it?
# -How does the program know that all stations as part of a template actually recorded the same event? is this specified in the database?
fig = tribe[0].st.plot(equal_scale=False, size=(800, 600))

# - removes templates from the tribe that contain fewer than 5 channels. why?
tribe.templates = [t for t in tribe if len({tr.stats.station for tr in t.st}) >= 5]
print(tribe)

# -Runs each template in the tribe over the data stored/ specified in the template and finds matches based on the specified filters
# -Stores the matches as detection objects which are stored in family objects with their template. the families are stored within a party object
# -endtime - starttime has to be the same as the tribe's process_length or else what?
# -threshold is how fussy the program is with 7 being really not that fussy and 12 being super fussy. 9 is pretty good.
# -Trig_int is the minimum ammount of time between detections for a single template. needed so it doesnt pick up the same waveform multiple times
# -Return_stream will return the raw data from the client that the template ran over if set to true
# -does this run through twice? once for each of the two days? because it says it made 16 detections and then 0 detections.
party, st = tribe.client_detect(
    client=client, starttime=t1, endtime=detection_endtime, threshold=9.,
    threshold_type="MAD", trig_int=2.0, plot=False, return_stream=True)
# -Plots cumulative detections over time
fig = party.plot(plot_grouped=True)
family = sorted(party.families, key=lambda f: len(f))[-1]
print(family)

# -Whats's the red?
# -Displays template
# -If the above is true why does it only show one detection? when it "Made 16 detections from 3 templates"
fig = family.template.st.plot(equal_scale=False, size=(800, 600))
streams = family.extract_streams(stream=st, length=10, prepick=2.5)
print(family.detections[0])

# - this is the unpolished image of the wave form where the template match was found.
# -Again, why is there only one detection shown?
fig = streams[family.detections[0].id].plot(equal_scale=False, size=(800, 600))
# -Wierdness going on here?
# -"Multiple picks found for WIZ.HHZ, using earliest"?
# -"WARNING Cannot check if cccsum is better, used 7 channels for detection"?
# -best way to save party data?
st = st.merge()
    
repicked_catalog += party.lag_calc(st, pre_processed=False, shift_len=0.5, min_cc=0.4)

# -assuming error "IndexError: list index out of range" comes from there being no repicked events in the catalog. Why not?
# is it because the include arrivals parameter has been removed from the catalog creation?
print(repicked_catalog[0].picks[0])
print(repicked_catalog[0].picks[0].comments[0])
print('done')
tribe = Tribe().read(fname)
catalog.write(fname, 'QUAKEML')
from obspy import read_events
catalog = read_events(fname)

