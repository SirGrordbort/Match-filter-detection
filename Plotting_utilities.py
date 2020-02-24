"""
a number of functions useful for plotting detections over time

:author: Toby Messerli
:date: 13/2/2020
"""

import datetime
# makes the text associated with each item in the legend
def make_legend_title(family):
    """
                    creates and returns a string based on the date of the family template and the number of detections
                    in the family

                        :type family: eqcorrscan template
                        :param family: the famly from which the template time is obtained
            """
    time = family.template.event.preferred_origin().time.datetime
    time_string = str(time.year)[2:4] + "/" + str(time.month) + "/" + str(time.day) + " " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + "."
    num_detections = len(family.detections)
    return time_string + " " + str(num_detections) + " detections"

def format_axis_and_legend(ax, lines_for_legend, legend_titles):
    """
                        ensures the given axes are properly laid out on the plot

                            :type ax: matplotlib axis object
                            :param ax: the axes on which to arrange the axes titles and legend position
                            :type lines_for_legend: a list of some sort of matplotlib lines
                            :param lines_for_legend: used to create the matplotlib legend object
                            :type legend_titles: list of strings
                            :param legend_titles: used to create the matplotlib legend object
                """
    # sets x and y axis labels
    ax.set_xlabel('date')
    ax.set_ylabel('detection number')

    # sets position for the legend
    box = ax.get_position()
    ax.set_ylim(ymin=0)
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # adds the legend
    ax.legend(lines_for_legend, legend_titles, bbox_to_anchor=(1, 1), markerscale=1)

def get_plottable_lists(date_and_index_list):
    """
                        makes lists of dates and detection numbers

                            :type date_and_index_list: a list of objects that contain a date along with how many
                            detections came before that date (index)
                            :param date_and_index_list: DateAndIndex objects obtained and split into useful lists
                """
    family_datetimes = []  # datetime objects. To be filled from DateAndIndex objects
    cumulative_detections = []  # integers. Filled from DateAndIndex objects. Represents total cumulative detections
    detections = []  # integers. Filled from count. Represents cumulative detections from a single family
    count = 0  # represents the number of cumulative detections for each individual family
    for date_and_index in date_and_index_list:
        count += 1
        family_datetimes.append(date_and_index.get_time())
        cumulative_detections.append(date_and_index.get_index())  # represents the total cumulative detections
        detections.append(count)
    return family_datetimes, cumulative_detections, detections

def add_eruptions(plt, lines_for_legend, legend_titles):
    """
                            adds vertical black dashed line at the white island eruption time

                                :type plt: a matplotlib plot
                                :param plt: the plot on which to add the line
                                :type lines_for_legend: list of some sort of matplotlib lines
                                :param lines_for_legend: the eruption line is added to this
                                :type legend_titles: list of strings
                                :param legend_titles: "white island eruption" is added to this
                    """
    eruption_time = datetime.datetime(2019, 12, 9, 14, 11)
    lines_for_legend.append(plt.axvline(eruption_time, ymin=0, ls="--", label="eruption", color="black", lw=1))
    legend_titles.append("white island eruption")

def plot_templates(plt, fam_plot_info):
    """
                                adds a vertical line to the plot where the date is that of a template
                        """
    template_time = fam_plot_info.family.template.event.preferred_origin().time.datetime
    plt.axvline(template_time, ymin=0, ls='-', c=fam_plot_info.color, alpha=1,
                lw=1)