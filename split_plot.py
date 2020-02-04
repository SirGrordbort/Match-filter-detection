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
    # plotting the cumulative detections for each family and getting the shapes and colors for use in the legend
    lines_for_legend.append(ax.plot(plot_lists[0], plot_lists[2], ls = '-',c = color)[0])
    # adding labels to the legend
    legend_titles.append(Plotting_utilities.make_legend_title(fam_plot_info.family))
    # adds a vertical line at the location of each template
    Plotting_utilities.plot_templates(plt,fam_plot_info)
# displays a black dotted vertical line at the date of the white island eruption
Plotting_utilities.add_eruptions(plt,lines_for_legend,legend_titles)
# format axes
Plotting_utilities.format_axis_and_legend(ax,lines_for_legend, legend_titles)
plt.show()
