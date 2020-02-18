from obspy import read_events
from obspy.clients.fdsn import Client
from matplotlib import pyplot as plt
import plot_event


def process_events(event_list, client, save_folder):
    event_num = 0
    for event in event_list:
        print("processing event "+str(event_num)+" out of "+str(len(event_list))+" events")
        event_num+=1
        try:
            fig = plot_event.plot_event_from_client(event, client,length=100)
        except IndexError:
            plt.close(plt.gcf())
            print("no picks")
            continue
        plt.savefig(save_folder+"/picks_{0}".format(event.preferred_origin().time.ctime()))
        plt.close(plt.gcf())