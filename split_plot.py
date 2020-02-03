from matplotlib import pyplot as plt
import prep_4_plotting

def make_legend_title(family):
    time = family.template.event.preferred_origin().time.datetime
    time_string = str(time.year)[2:4] + "/" + str(time.month) + "/" + str(time.day) + " " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + "."
    num_detections = len(family.detections)
    return time_string + " " + str(num_detections) + " detections"

fam_plot_infos = prep_4_plotting.prep("year_det_and_temp_party.tgz")
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])
lines_for_legend = []
legend_titles = []
# runs through each family list of dateAndIndex objects and splits them into a list of datetime objects and corresponding
# index objects which represent the total number of detections to that date
for fam_plot_info in fam_plot_infos:
    date_and_index_list = fam_plot_info.detection_list
    family_datetimes = []
    detection_num = []
    count = 0
    for date_and_index in date_and_index_list:
        count+=1
        family_datetimes.append(date_and_index.get_time())
        detection_num.append(count)
    style, color = prep_4_plotting.LineType.next_line()
    lines_for_legend.append(ax.plot(family_datetimes, detection_num, ls = style,c = color,s = 1))
    template_time = fam_plot_info.family.template.event.preferred_origin().time.datetime
    legend_titles.append(make_legend_title(fam_plot_info.family))
    plt.axvline(template_time, ymin=0, ls='-', c=color, alpha=1) # adds a vertical line at the location of each template

# format axes
ax.set_xlabel('date')
ax.set_ylabel('detection number')
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
legend = ax.legend(lines_for_legend, legend_titles, bbox_to_anchor=(1, 1), markerscale = 10 )
plt.show()