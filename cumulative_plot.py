"""
Makes a plot of cumulative eqcorrscan detections over time. Just plots overall cumulative detections

:author: Toby Messerli
:date: 13/2/2020
"""
from matplotlib import pyplot as plt
import prep_4_plotting
import Plotting_utilities


fam_plot_infos = prep_4_plotting.prep("year_party_1.tgz")
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])
lines_for_legend = []
legend_titles = []
# runs through each family list of dateAndIndex objects and splits them into a list of datetime objects and corresponding
# index objects which represent the total number of detections to that date
for fam_plot_info in fam_plot_infos:
    plot_lists = Plotting_utilities.get_plottable_lists(fam_plot_info.detection_list)
    color = fam_plot_info.color
    # plotting the total cumulative detections and getting the shapes and colors for use in the legend
    lines_for_legend.append(ax.scatter(plot_lists[0], plot_lists[1], marker=',',s = 1, c=color))
    # adding labels to the legend
    legend_titles.append(Plotting_utilities.make_legend_title(fam_plot_info.family))
    # displays vertical lines at each template date
    Plotting_utilities.plot_templates(plt,fam_plot_info)
# displays a black dotted vertical line at the date of the white island eruption
Plotting_utilities.add_eruptions(plt,lines_for_legend,legend_titles)
# format axes
Plotting_utilities.format_axis_and_legend(ax, lines_for_legend,legend_titles)
plt.show()