# makes the text associated with each item in the legend
def make_legend_title(family):
    time = family.template.event.preferred_origin().time.datetime
    time_string = str(time.year)[2:4] + "/" + str(time.month) + "/" + str(time.day) + " " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + "."
    num_detections = len(family.detections)
    return time_string + " " + str(num_detections) + " detections"

def format_axis_and_legend(ax, lines_for_legend, legend_titles):
    ax.set_xlabel('date')
    ax.set_ylabel('detection number')
    box = ax.get_position()
    ax.set_ylim(ymin=0)
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    legend = ax.legend(lines_for_legend, legend_titles, bbox_to_anchor=(1, 1), markerscale=1)