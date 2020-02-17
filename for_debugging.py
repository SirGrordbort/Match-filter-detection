from eqcorrscan import Party
from obspy import read
from obspy import Catalog
from obspy import Stream
import glob

import logging

logging.basicConfig(level="DEBUG")


# streams and parties are folders containing a stream and party file for each of 395 days
def repick_catalog(streams, parties):
    repicked_catalog = Catalog()
    # glob doesn't sort - this doesn't guarantee that the stream will correspond to the party - name your files something useful, like the start and end of the data...
    stream_files = sorted(glob.glob(streams + '/*.ms'))
    party_files = sorted(glob.glob(parties + '/*'))
    for stream_file, party_file in zip(stream_files, party_files):
        stream = read(stream_file)  # Adding to the stream will make it longer and longer and longer until RAM ist kaput... Not what you want
        stream = stream.merge()  # Needs to be a merged stream
        party = Party().read(party_file)  # Similarly you don't want to add to the party...
        party = Party([f for f in party if len(f) > 0])  # Removing empty families to get rid of some complaining output
        _catalog = party.lag_calc(stream, pre_processed=False, shift_len=0.5, min_cc=0.4)
        repicked_catalog += _catalog

    repicked_catalog.write("repicked_catalog", "QUAKEML")


if __name__ == "__main__":
    repick_catalog("streams4debug", "partys4debug")
