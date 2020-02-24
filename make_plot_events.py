"""
creates lists of plot event objects and the objects themselves which hold events and their associated picks and repicks
:author: Toby Messerli
:date: 13/2/2020
"""

class PlotEvent:
    """
    stores events along with the picks and repicks associated with it
    """
    def __init__(self, event, picks, repicks):
        self.event = event
        self.picks = picks
        self.repicks = repicks
        self.all_picks = []
        for pick in picks:
            self.all_picks.append(pick)
        for repick in repicks:
            self.all_picks.append(repick)



def make_plot_events(repicked_events, events):
    """
    creates a list of PlotEvent objects
                :return: List of PlotEvent objects
                :type repicked_events: list of EQcorrscan events
                :param repicked_events: events who's picks have been re-evaluated by the eqcorrscan lag_calc method
                :type events: list of EQcorrscan events
                :param events: list of the same events as in repicked events but who's picks have not been re-evaluated
    """
    plot_events = []
    event_num = 0
    count = 0
    count2 = 0
    for event in events:
        print("event num " + str(event_num))
        event_num += 1
        for repicked_event in repicked_events:
            count2 += 1
            if repicked_event.resource_id == event.resource_id:
                count +=1
                repicked_events.remove(repicked_event)
                plot_events.append(PlotEvent(repicked_event, event.picks, repicked_event.picks))
                break
    return plot_events

