"""
a script for improving the picks on streams
:author: Toby Messerli
:date: 13/2/2020
"""
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
    """
                improves the pick location of the events in the parties on the streams and saves an image of the original
                and improved pick on the stream
                    :type streams: a folder containing obspy stream files
                    :type parties: a folder containing eqcorrscan party objects

                    Note: it is important that the stream and party folders contain streams and parties named in such a
                    way that when sorted by name the first party is associated with the first stream and so on

                    Note: not all picks will have associated repicks. this is because the minimum cross corelation value
                    is too low for some repicks

                    Note: the repicked images will be saved to different files depending on whether they have repicks
                    and whether the repicks are different from the originals

                    Note: the repicks are often just a few microseconds different from the original


        """
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
        # adding origins to the events in the party. these origins are located where the events template is located but
        # the time is adjusted from the templates origin time
        Add_basic_origins.add_origins(False, party)

        try:
            party_copy = party.copy()  # copying party to ensure its picks are different from the repicks
            party_catalog = party_copy.get_catalog()
            _catalog = party.lag_calc(stream, pre_processed=False, shift_len=0.5, min_cc=0.4)  # repicking

            # groups events with their pre and post picks
            plot_events = make_plot_events(_catalog.events, party_catalog.events)

            for plot_event in plot_events:

                # ensures the event has picks associated with it
                if plot_event.all_picks is not None and len(plot_event.all_picks) > 0:
                    st = prep_stream(stream, plot_event.all_picks)  # gets the relevant channels from the stream
                    plot_picks_from_stream(plot_event, st, length=100)  # creates the picks on stream plot

                    # checks whether any of the repicks have actually changed from the originals or if there are any
                    # repicks at all
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
                    plt.close(plt.gcf())  # closes current figure to stop ram running out
        except(AssertionError):
            print("Skipped day")  # FIXME skips 3 days due to rounding errors updating eqcorrscan should fix this
            continue

        repicked_catalog += _catalog
        print("day: " + str(count))

    repicked_catalog.write("repicked_catalog2", "QUAKEML")


if __name__ == "__main__":
    repick_catalog("streams", "partys")
