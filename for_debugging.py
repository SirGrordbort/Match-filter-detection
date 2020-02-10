from eqcorrscan import Party
from obspy import read
from obspy import Catalog
from obspy import Stream
import glob


# streams and parties are folders containing a stream and party file for each of 395 days
def repick_catalog(streams, parties):
    repicked_catalog = Catalog()
    stream = Stream()
    party = Party()
    for stream_file, party_file in zip(glob.glob(streams + "/*"), glob.glob(parties + "/*")):
        stream += read(stream_file)
        party += Party().read(party_file)
        _catalog = party.lag_calc(stream, pre_processed=False, shift_len=0.5, min_cc=0.4)
        repicked_catalog.extend(_catalog)

    repicked_catalog.write("repicked_catalog", "QUAKEML")


if __name__ == "__main__":
    repick_catalog("streams4debug", "partys4debug")
