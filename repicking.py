from eqcorrscan import Party
from obspy import read, UTCDateTime
from obspy import Catalog
from obspy import Stream
import glob
from Add_basic_origins import add_origins





def repick_catalog(streams, parties, start_date):
    day_len = 86400
    repicked_catalog = Catalog()
    party_list = []
    for party_file in glob.glob(parties + "/*"):
        party_list.append(Party().read(party_file))
    count = -1
    num_sliced = 1
    stream = Stream()

    for stream_file in glob.glob(streams + "/*"):
        count += 1
        stream += read(stream_file)
        if count >= 3:
            print("slicing stream")
            stream.slice(start_date+day_len*num_sliced)
            num_sliced += 1
        if count >= 1:
            party = party_list[count-1]
            add_origins(False, party)
            print("lag_calcing")
            _catalog = party.lag_calc(stream, pre_processed=False, shift_len=0.5, min_cc=0.4)
            repicked_catalog.extend(_catalog)

    repicked_catalog.write("repicked_catalog", "QUAKEML")

if __name__ == "__main__":
    date = UTCDateTime(2018, 12, 9)
    repick_catalog("streams", "partys",date )
