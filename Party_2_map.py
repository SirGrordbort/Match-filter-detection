"""
creates an ArcGIS map from an eqcorrscan party. Map features have the following fields:
Describe: a string with some basic descriptive information about the event
Magnitude: magnitude of the event
Depth: depth of the event
Time: time the event occured
Is_template: whether the event is also an eqcorrscan template
family: which family within the party the event belongs to

Note: must be used with ArcGIS pro. Add this as a script and add two parameters. The first must be a file and the second
a folder where the output feature class will go. This feature class must then be added to the map before it is visible

:author: Toby Messerli
:date: 13/2/2020
"""

import arcpy
from eqcorrscan import Party

# the party to add to the map
input_file = arcpy.GetParameterAsText(0)

# the file location of the party feature class
output_file = arcpy.GetParameterAsText(1)

party = Party().read(input_file)
# creates the feature class and corresponding fields for the party
earthquakes = arcpy.CreateFeatureclass_management(output_file, "events", "POINT", "", "DISABLED", "DISABLED", "wgs84.prj", "", "","", "", "")
arcpy.AddField_management(earthquakes, "Describe", "TEXT")
arcpy.AddField_management(earthquakes, "Magnitude", "DOUBLE")
arcpy.AddField_management(earthquakes, "Depth", "DOUBLE")
arcpy.AddField_management(earthquakes, "Time", "DATE")
arcpy.AddField_management(earthquakes, "Is_template", "TEXT")
arcpy.AddField_management(earthquakes, "family", "TEXT")

# adds a row of fields to the feature class
def make_fields(is_template, eq_cursor, event, time, family):
    """
                adds the relevant fields to the cursor which adds them to its feature class

                    :type is_template: boolean
                    :param is_template: whether the event that is passed in is the event from an eqcorrscan template
                    :type eq_cursor: an arcpy.da.insertcursor
                    :param eq_cursor: represents a row in an arcpy feature class that can be inserted
                    :type event: an obspy event
                    :param event: information from this event is passed to the eq_cursor
                    :type time: python datetime object
                    :param time: the time at which the event occurred
                    :type family: eqcorrscan family
                    :param family: the family the event belongs to, added to the cursor
        """
    origin = event.preferred_origin()
    mag = event.preferred_magnitude()  # this will often be none for the events unless they are a template event
    if mag is not None:
        mag = mag.mag
    desc = event.short_str()
    if origin is not None:
        point = arcpy.Point(origin.longitude, origin.latitude)
        shape = arcpy.PointGeometry(point)
        depth = event.preferred_origin().depth
        eq_cursor.insertRow((shape, desc, mag, depth, time, is_template, family))
    else:
        # makes a skeleton row for events without an origin
        eq_cursor.insertRow((None, desc, None, None, time, is_template, family))

eq_cursor = arcpy.da.InsertCursor(earthquakes, ("Shape", "Describe", "Magnitude", "Depth", "Time","Is_template","family",))
try:
    for fam in party.families:
        template_event = fam.template.event
        template_origin = template_event.preferred_origin()
        if template_origin is None:
            raise RuntimeError("origin for template should not be none")
        time = template_origin.time.datetime
        make_fields("True", eq_cursor, template_event, time, fam.template.name)


        for detection in fam.detections:
            event = detection.event
            time = detection.detect_time.datetime
            make_fields("False", eq_cursor, event, time, family = fam.template.name)
finally:
    del eq_cursor  # deletes the cursor under all conditions to prevent memory leaks
