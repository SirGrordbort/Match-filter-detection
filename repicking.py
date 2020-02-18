from eqcorrscan import Party
from obspy import read
from obspy import Catalog
from obspy import Stream
import glob
import logging
import Add_basic_origins
from make_plot_events import make_plot_events
from multi_picks_on_stream import plot_event_from_client
from obspy.clients.fdsn import Client

# debugged by calum
logging.basicConfig(level="DEBUG")


# streams and parties are folders containing a stream and party file for each of 395 days
def repick_catalog(streams, parties):
    client = Client("http://service.geonet.org.nz")
    repicked_catalog = Catalog()
    # glob doesn't sort - this doesn't guarantee that the stream will correspond to the party - name your files something useful, like the start and end of the data...
    stream_files = sorted(glob.glob(streams + '/*.ms'))

    party_files = sorted(glob.glob(parties + '/*'))
    count = 0

    for stream_file, party_file in zip(stream_files, party_files):
        count += 1
        stream = read(stream_file)  # Adding to the stream will make it longer and longer and longer until RAM ist kaput... Not what you want
        stream = stream.merge()  # Needs to be a merged stream
        party = Party().read(party_file)  # Similarly you don't want to add to the party...
        party = Party([f for f in party if len(f) > 0])  # Removing empty families to get rid of some complaining output
        Add_basic_origins.add_origins(False, party)

        try:
            party_catalog = party.get_catalog()
            _catalog = party.lag_calc(stream, pre_processed=False, shift_len=0.5, min_cc=0.4)
            plot_events = make_plot_events(_catalog.events, party_catalog.events)
            for plot_event in plot_events:
                if plot_event.all_picks is not None:
                    plot_event_from_client(plot_event,client,length=100)
        except(AssertionError):
            print("Skipped day")
            continue

        repicked_catalog += _catalog
        print("day: "+ str(count))

    repicked_catalog.write("repicked_catalog", "QUAKEML")


if __name__ == "__main__":
    repick_catalog("streams", "partys")
