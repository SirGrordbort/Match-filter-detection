
from matplotlib import pyplot as plt
import prep_4_plotting
import datetime
import Plotting_utilities


# prepares the data in the given party for plotting
fam_plot_infos = prep_4_plotting.prep("test_party.tgz")
# sets up the initial figure and axes
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])

#lists for storing the items that make up the items in the legend i.e. the text and lines/shapes
lines_for_legend = []
legend_titles = []

# runs through each family list of dateAndIndex objects and splits them into a list of datetime objects and corresponding
# index objects which represent the total number of detections to that date
for fam_plot_info in fam_plot_infos:
    date_and_index_list = fam_plot_info.detection_list
    family_datetimes = []
    cumulative_detections = []
    detections = []
    count = 0 # represents the number of cumulative detections for each individual family
    for date_and_index in date_and_index_list:
        count += 1
        family_datetimes.append(date_and_index.get_time())
        cumulative_detections.append(date_and_index.get_index()) # represents the total cumulative detections
        detections.append(count)
    color = fam_plot_info.color # the color associated with a given family (template and its detections)

    # plotting the total cumulative detections and getting the shapes and colors for use in the legend
    lines_for_legend.append(ax.scatter(family_datetimes, cumulative_detections, marker=',',s = 10, c=color))

    # plotting the individual families with their cumulative detections
    ax.plot(family_datetimes, detections, ls = '-',c = color)

    # adding labels to the legend
    legend_titles.append(Plotting_utilities.make_legend_title(fam_plot_info.family))

    template_time = fam_plot_info.family.template.event.preferred_origin().time.datetime
    plt.axvline(template_time, ymin=0, ls='-', c=color, alpha=1,lw = 1) # adds a vertical line at the location of each template

#adding the eruption to the graph and legend
eruption_time = datetime.datetime(2019,12,9,14,11)
lines_for_legend.append(plt.axvline(eruption_time, ymin = 0, ls = "--", label = "eruption", color = "black", lw = 1))
legend_titles.append("white island eruption")

# format axes and legend
Plotting_utilities.format_axis_and_legend(ax, lines_for_legend, legend_titles)
plt.show()
