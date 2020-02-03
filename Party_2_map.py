import arcpy
from eqcorrscan import Party

# the party to add to the map
input_file = arcpy.GetParameterAsText(0)

# the file location of the party feature class
output_file = arcpy.GetParameterAsText(1)

party = Party().read(input_file)
# creates the feature class and corresponding fields for the party
earthquakes = arcpy.CreateFeatureclass_management(output_file, "events", "POINT", "", "DISABLED", "DISABLED", "wgs84.prj", "", "","", "", "")
arcpy.AddField_management(earthquakes, "Describe", "STRING")
arcpy.AddField_management(earthquakes, "Magnitude", "Double")
arcpy.AddField_management(earthquakes, "Depth", "Double")
arcpy.AddField_management(earthquakes, "Time", "String")
arcpy.AddField_management(earthquakes, "Is_template", "String")


# adds a row of fields to the feature class
def make_fields(is_template, eq_cursor, event, time):
    origin = event.preferred_origin()
    desc = event.short_str()
    if origin is not None:
        point = arcpy.Point(origin.longitude, origin.latitude)
        shape = arcpy.PointGeometry(point)
        mag = event.preferred_magnitude().mag
        depth = event.preferred_origin().depth
        eq_cursor.insertRow((shape, desc, mag, depth, time, is_template))
    else:
        eq_cursor.insertRow((None, desc, None, None, time, is_template))
arcpy.AddMessage("party:" + str(party))

eq_cursor = arcpy.da.InsertCursor(earthquakes, ("Shape", "Describe", "Magnitude", "Depth", "Time","Is_template",))
try:
    for fam in party.families:
        template_event = fam.template.event
        template_origin = template_event.preferred_origin()
        if template_origin is None:
            raise RuntimeError("origin for template should not be none")
        time = template_origin.time.isoformat(sep=' ')
        make_fields("True", eq_cursor, template_event, time)


        for detection in fam.detections:
            event = detection.event
            time = detection.detect_time.isoformat(sep=' ')
            make_fields("False", eq_cursor, event, time)
finally:
    del eq_cursor
