"""
Makes a plot of cumulative eqcorrscan detections over time. on the same set of axis the plot contains both overall
cumulative detections and those for each family

:author: Toby Messerli
:date: 13/2/2020
"""
from matplotlib import pyplot as plt
import prep_4_plotting
import Plotting_utilities


# prepares the data in the given party for plotting
fam_plot_infos = prep_4_plotting.prep("party.tgz")
# sets up the initial figure and axes
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])

#lists for storing the items that make up the items in the legend i.e. the text and lines/shapes
lines_for_legend = []
legend_titles = []

# runs through each family list of dateAndIndex objects and splits them into a list of datetime objects and corresponding
# index objects which represent the total number of detections to that date
for fam_plot_info in fam_plot_infos:
    plot_lists = Plotting_utilities.get_plottable_lists(fam_plot_info.detection_list)
    color = fam_plot_info.color # the color associated with a given family (template and its detections)

    # plotting the total cumulative detections and getting the shapes and colors for use in the legend
    lines_for_legend.append(ax.scatter(plot_lists[0], plot_lists[1], marker=',',s = 10, c=color))

    # plotting the individual families with their cumulative detections
    ax.plot(plot_lists[0], plot_lists[2], ls = '-',c = color)

    # adding labels to the legend
    legend_titles.append(Plotting_utilities.make_legend_title(fam_plot_info.family))

    Plotting_utilities.plot_templates(plt, fam_plot_info) # adds a vertical line at the location of each template

#adding the eruption to the graph and legend
Plotting_utilities.add_eruptions(plt,lines_for_legend,legend_titles)

# format axes and legend
Plotting_utilities.format_axis_and_legend(ax, lines_for_legend, legend_titles)
plt.show()
