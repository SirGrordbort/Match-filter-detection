import multi_picks_on_stream

class PlotEvent:
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

