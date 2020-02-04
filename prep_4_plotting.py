import cartopy
from eqcorrscan import Party

import math


# class for giving a new line type every time next line is called also gives out colors and line styles
class LineType:
    def __init__(self):
        self.colors = ['red', 'green', 'blue', 'cyan', 'magenta',
                       'black', 'firebrick', 'purple', 'darkgoldenrod', 'gray', 'rosybrown', 'lightcoral', 'salmon',
                       "orangered", "sienna", "orange", "gold", "olive", "lawngreen", "palegreen", "springgreen",
                       "darkslategray", "steelblue", "navy", "plum", "deeppink"]
        self.num_color_calls = 0 # how many times an instance of this class has been asked for a color
        self.linestyles = [':', '-', '--', '-.']
        self.num_calls = 0  # how many times an instance of this class has been called on to provide a new line style
        self.line_index = 0  # the index in the line styles list of the last line style to be sent out
        self.col_index = 0  # the index in the color list of the last line color to be sent out


    # turns the number of times this class has been called on for a new line type into an index for each list
    def num_calls_to_2D(self):
        self.line_index = math.floor(self.num_calls / len(self.colors))
        self.col_index = self.num_calls - 11 * self.line_index


    def next_line(self):
        # when all line types have been exhasted throws an error if another type is requested
        if self.line_index > 3:
            raise RuntimeError("out of line types!")

        color = self.colors[self.col_index]
        style = self.linestyles[self.line_index]
        self.num_calls += 1
        self.num_calls_to_2D()
        return style, color

    # returns the next color in the list of colors
    def next_color(self):
        if self.num_color_calls >= len(self.colors):
            raise RuntimeError("out of colors!")
        else:
            color = self.colors[self.num_color_calls]
        self.num_color_calls += 1
        return color

# class for grouping datetime objects together with their corresponding cumulative detections
# useful because when the cumulative detections (index) is changed in an instance of this class it changes for this
# instance in every list this instance is found in
class DateAndIndex:
    def __init__(self, datetime):
        self.time = datetime
        self.index = None

    def set_index(self, index):
        self.index = index

    def get_index(self):
        if self.index is None:
            raise RuntimeError("index is None")
        else:
            return self.index

    def get_time(self):
        return self.time

# class that groups information to be plotted together
class FamPlotInfo:
    def __init__(self, family, detection_list, color):
        self.family = family
        self.detection_list = detection_list
        self.color = color
        # already contained within the family object but makes sorting lists of this class easier
        self.template_time = family.template.event.preferred_origin().time.datetime


def prep(party_name):
    party = Party().read(party_name)
    line_types = LineType()
    all_dates = []  # stores the date of every event in the party
    fam_plot_info_list = []  # stores all lists of dates for each family
    for fam in party.families:
        fam_dates = []  # stores the datetime objects for all events in a family
        for detection in fam.detections:
            time = detection.detect_time.datetime  # gets each detection time
            datetime = DateAndIndex(time)  # adds it to a DateAndIndex object so it can be plotted in the correct location
            fam_dates.append(datetime)
            all_dates.append(datetime)
        fam_dates.sort(key=lambda x: x.get_time()) # sorts each family of events by date
        fam_plot_info = FamPlotInfo(fam, fam_dates, line_types.next_color())
        fam_plot_info_list.append(fam_plot_info)

    fam_plot_info_list.sort(key=lambda fam_plot_info: fam_plot_info.template_time)
    all_dates.sort(key=lambda x: x.get_time())
    # runs through the list of dateAndIndex objects and adds the index to the object the index will be added to the objects stored
    # in the individual family lists as well (because both lists store the same objects) this allows the date from each family
    # list to be plotted with the correct number of cumulative detections
    index = 0
    for date_and_index in all_dates:
        index += 1
        date_and_index.set_index(index)
    return fam_plot_info_list


