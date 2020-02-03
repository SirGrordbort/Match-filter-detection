
from matplotlib import pyplot as plt
import prep_4_plotting
import datetime

def make_legend_title(family):
    time = family.template.event.preferred_origin().time.datetime
    time_string = str(time.year)[2:4] + "/" + str(time.month) + "/" + str(time.day) + " " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + "."
    num_detections = len(family.detections)
    return time_string + " " + str(num_detections) + " detections"

fam_plot_infos = prep_4_plotting.prep("year_party_1.tgz")
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])
lines_for_legend = []
legend_titles = []
# runs through each family list of dateAndIndex objects and splits them into a list of datetime objects and corresponding
# index objects which represent the total number of detections to that date
for fam_plot_info in fam_plot_infos:
    date_and_index_list = fam_plot_info.detection_list
    family_datetimes = []
    cumulative_detections = []
    for date_and_index in date_and_index_list:
        family_datetimes.append(date_and_index.get_time())
        cumulative_detections.append(date_and_index.get_index())
    color = fam_plot_info.color
    lines_for_legend.append(ax.scatter(family_datetimes, cumulative_detections, marker=',',s = 1, c=color))
    template_time = fam_plot_info.family.template.event.preferred_origin().time.datetime
    legend_titles.append(make_legend_title(fam_plot_info.family))
    plt.axvline(template_time, ymin=0, ls='-', c=color, alpha=1) # adds a vertical line at the location of each template
eruption_time = datetime.datetime(2019,12,9,14,11)
lines_for_legend.append(plt.axvline(eruption_time, ymin = 0, ls = "--", label = "eruption", color = "black", lw = 1))
legend_titles.append("white island eruption")
# format axes
ax.set_xlabel('date')
ax.set_ylabel('detection number')
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
legend = ax.legend(lines_for_legend, legend_titles, bbox_to_anchor=(1, 1), markerscale = 10 )
plt.show()