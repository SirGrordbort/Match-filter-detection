from eqcorrscan import Party
from obspy import read
from obspy import Catalog
from obspy import Stream
import glob
import logging
import Add_basic_origins
from make_plot_events import make_plot_events
from multi_picks_on_stream import plot_picks_from_stream
from matplotlib import pyplot as plt

# debugged by calum
logging.basicConfig(level="DEBUG")

def prep_stream(stream, picks):
    wav_ids = [pick.waveform_id for pick in picks]
    st = Stream()
    for wav in wav_ids:
        trace_id = wav.network_code +"."+wav.station_code +"."+wav.location_code +"."+wav.channel_code
        st += stream.select(id = trace_id)
    return st

# streams and parties are folders containing a stream and party file for each of 395 days
def repick_catalog(streams, parties):
    repicked_catalog = Catalog()

    # all the stream and party files for the year and month
    stream_files = sorted(glob.glob(streams + '/*.ms'))
    party_files = sorted(glob.glob(parties + '/*'))

    count = 0
    for stream_file, party_file in zip(stream_files, party_files):
        count += 1
        # prepping streams and parties for processing
        stream = read(stream_file)
        stream = stream.merge()
        party = Party().read(party_file)
        party = Party([f for f in party if len(f) > 0])  # Removing empty families to get rid of some complaining output
        Add_basic_origins.add_origins(False, party)

        try:
            party_copy = party.copy()  # copying party to ensure its picks are different from the repicks
            party_catalog = party_copy.get_catalog()
            _catalog = party.lag_calc(stream, pre_processed=False, shift_len=0.5, min_cc=0.4)  # repicking

            # creates events combined with their pre and post picks
            plot_events = make_plot_events(_catalog.events, party_catalog.events)

            for plot_event in plot_events:

                # ensures the event has picks associated with it
                if plot_event.all_picks is not None and len(plot_event.all_picks) > 0:
                    st = prep_stream(stream, plot_event.all_picks)  # gets the relevant channels from the stream
                    plot_picks_from_stream(plot_event, st, length=100)  # creates the picks on stream plot

                    # checks whether any of the repicks have actually changed
                    altered = False
                    for pick in plot_event.picks:
                        if pick.time.datetime not in [repick.time.datetime for repick in plot_event.repicks]:
                            altered = True
                            break
                    if len(plot_event.repicks) == 0:
                        altered_pick = "no_repicks"
                    elif altered is True:
                        altered_pick = "altered_picks"
                    elif altered is False:
                        altered_pick = "unaltered_picks"

                    plt.savefig(
                        "repicked_events/" + altered_pick + "/" + plot_event.event.preferred_origin().time.ctime())
                    plt.close(plt.gcf())
        except(AssertionError):
            print("Skipped day")  # FIXME skips 3 days due to rounding errors
            continue

        repicked_catalog += _catalog
        print("day: " + str(count))

    repicked_catalog.write("repicked_catalog2", "QUAKEML")


if __name__ == "__main__":
    repick_catalog("streams", "partys")
