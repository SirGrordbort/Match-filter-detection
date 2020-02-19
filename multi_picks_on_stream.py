#TODO properly credit calums work

import numpy as np


def plot_picks_from_client(pick_event, client, length=60, size=(10.5, 10.5),
                           all_channels=False, filt=None, ignore_rotated=True,
                           return_stream=False):
    """
    Plot the waveforms for an event with pick and calculated arrival times.

    :type event: `obspy.core.event.Event`
    :param event: Event to plot
    :param client: An obspy client with `get_waveforms_bulk` method
    :type length: float
    :param length: Length to plot, from origin time.
    :type all_channels: bool
    :param all_channels: Whether to download all channels from that sensor.
    """
    from obspy import Stream
    from obspy.clients.fdsn.client import FDSNNoDataException, FDSNException

    try:
        origin_time = pick_event.event.preferred_origin().time or pick_event.event.origins[0].time
    except AttributeError:
        # If there isn't an origin time, use the start of the stream
        origin_time = min([pick.time for pick in pick_event.all_picks])
    t1 = origin_time - length / 10
    t2 = t1 + length
    bulk = []
    for pick in pick_event.all_picks:
        if all_channels and pick.waveform_id.channel_code:
            channel = "{0}?".format(pick.waveform_id.channel_code[0:2])
        else:
            channel = pick.waveform_id.channel_code or "*"
        chan_info = (pick.waveform_id.network_code or "*",
                     pick.waveform_id.station_code or "*",
                     pick.waveform_id.location_code or "*", channel,
                     t1, t2)
        if ignore_rotated and channel[-1] in ["R", "T"]:
            continue
        if chan_info not in bulk:
            bulk.append(chan_info)
    try:
        st = client.get_waveforms_bulk(bulk)
    except (FDSNNoDataException, FDSNException) as e:
        print("No data exception - trying individual channels")
        st = Stream()
        for chan_info in bulk:
            try:
                st += client.get_waveforms(
                    network=chan_info[0], station=chan_info[1],
                    location=chan_info[2], channel=chan_info[3],
                    starttime=chan_info[4], endtime=chan_info[5])
                print("Downloaded for {0}.{1}.{2}.{3}".format(*chan_info[0:4]))
            except FDSNNoDataException:
                print("No data for {0}.{1}.{2}.{3}".format(*chan_info[0:4]))
    if filt:
        st.detrend().filter('bandpass', freqmin=filt[0], freqmax=filt[1])
    if return_stream:
        return plot_event(pick_event, st, length=length, size=size), st,
    return plot_event(pick_event, st, length=length, size=size)


def plot_event(pick_event, st, length=60., size=(10.5, 10.5), fig=None):
    """
    Plot the waveforms for an event with pick and calculated arrival times.

    :type event: `obspy.core.event.Event`
    :param event: Event to plot
    :type st: `obspy.core.stream.Stream`
    :param st: Obspy Stream for this event
    :type length: float
    :param length: Length to plot, from origin time.
    """
    import matplotlib.pyplot as plt

    try:
        origin_time = pick_event.event.preferred_origin().time or pick_event.event.origins[0].time
    except AttributeError:
        # If there isn't an origin time, use the start of the stream
        origin_time = st[0].stats.starttime
    if length:
        st = st.slice(origin_time, origin_time + length)
    # Trim the event around the origin time
    fig = fig or plt.figure()
    fig.set_size_inches(size)
    axes = fig.subplots(len(st), 1, sharex=True)
    if len(st) == 1:
        axes = [axes]
    lines, labels = ([], [])
    min_x = []
    max_x = []
    for ax, tr in zip(axes, st):
        ax.cla()
        prepicks = []
        postpicks = []
        for pick in pick_event.picks:
            if pick.waveform_id.station_code == tr.stats.station:
                prepicks.append(pick)
        for pick in pick_event.repicks:
            if pick.waveform_id.station_code == tr.stats.station:
                postpicks.append(pick)
        lines, labels, chan_min_x, chan_max_x = _plot_channel(
            ax=ax, tr=tr, prepicks=prepicks, postpicks=postpicks,  lines=lines,
            labels=labels)
        min_x.append(chan_min_x)
        max_x.append(chan_max_x)
    axes[-1].set_xlim([np.min(min_x), np.max(max_x)])
    axes[-1].set_xlabel("Time")
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    fig.legend(lines, labels)
    return fig


def _plot_channel(ax, tr, prepicks, postpicks, lines=[], labels=[]):
    """ Plot a single channel into an axis object. """
    x = np.arange(0, tr.stats.endtime - tr.stats.starttime + tr.stats.delta,
                  tr.stats.delta)
    y = tr.data
    if len(x) > len(y):
        x = x[0:len(y)]
    elif len(x) < len(y):
        last_x = x[-1]
        for i in range(len(y) - len(x)):
            x.append(last_x + (tr.stats.delta * i))
    x = np.array([(tr.stats.starttime + _x).datetime for _x in x])
    min_x, max_x = (x[0], x[-1])
    ax.plot(x, y, 'k', linewidth=1.2)
    for pick in prepicks:
        if not pick.phase_hint:
            pcolor = 'k'
            label = 'Unknown pick'
        elif 'P' in pick.phase_hint.upper():
            pcolor = 'red'
            label = 'P-pick'
        elif 'S' in pick.phase_hint.upper():
            pcolor = 'blue'
            label = 'S-pick'
        else:
            pcolor = 'k'
            label = 'Unknown pick'
        line = ax.axvline(x=pick.time.datetime, color=pcolor, linewidth=2,
                          linestyle='--', label=label)
        if label not in labels:
            lines.append(line)
            labels.append(label)
        if pick.time.datetime > max_x:
            max_x = pick.time.datetime
        elif pick.time.datetime < min_x:
            min_x = pick.time.datetime


    for pick in postpicks:
        if not pick.phase_hint:
            pcolor = 'k'
            label = 'Unknown repick'
        elif 'P' in pick.phase_hint.upper():
            pcolor = 'yellow'
            label = 'P-repick'
        elif 'S' in pick.phase_hint.upper():
            pcolor = 'green'
            label = 'S-repick'
        else:
            pcolor = 'k'
            label = 'Unknown repick'
        line = ax.axvline(x=pick.time.datetime, color=pcolor, linewidth=2,
                          linestyle=':', label=label)
        if label not in labels:
            lines.append(line)
            labels.append(label)
        if pick.time.datetime > max_x:
            max_x = pick.time.datetime
        elif pick.time.datetime < min_x:
            min_x = pick.time.datetime
    ax.set_ylabel(tr.id, rotation=0, horizontalalignment="right")
    ax.yaxis.set_ticks([])
    return lines, labels, min_x, max_x