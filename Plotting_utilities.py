import datetime
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

def get_plottable_lists(date_and_index_list):
    family_datetimes = []
    cumulative_detections = []
    detections = []
    count = 0  # represents the number of cumulative detections for each individual family
    for date_and_index in date_and_index_list:
        count += 1
        family_datetimes.append(date_and_index.get_time())
        cumulative_detections.append(date_and_index.get_index())  # represents the total cumulative detections
        detections.append(count)
    return family_datetimes, cumulative_detections, detections

def add_eruptions(plt, lines_for_legend, legend_titles):
    eruption_time = datetime.datetime(2019, 12, 9, 14, 11)
    lines_for_legend.append(plt.axvline(eruption_time, ymin=0, ls="--", label="eruption", color="black", lw=1))
    legend_titles.append("white island eruption")

def plot_templates(plt, fam_plot_info):
    template_time = fam_plot_info.family.template.event.preferred_origin().time.datetime
    plt.axvline(template_time, ymin=0, ls='-', c=fam_plot_info.color, alpha=1,
                lw=1)