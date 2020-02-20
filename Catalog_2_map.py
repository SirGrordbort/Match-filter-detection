"""
creates an ArcGIS map from an obspy catalog, if at all possible use the party_2_map script as it is more reliable and
has more useful outputs

WARNING: does not currently work as intended. Use party_2_map instead

Note: must be used with ArcGIS pro. Add this as a script and add two parameters. The first must be a file and the second
a folder where the output feature class will go. This feature class must then be added to the map before it is visible
:author: Toby Messerli
:date: 13/2/2020
"""
import arcpy
from obspy import read_events

# FIXME update to be similar to party_2_map
# The file location of the obspy event catalog
input_file = arcpy.GetParameterAsText(0)

# The output feature class
earthquakes = arcpy.GetParameter(1)

catalog = read_events(input_file)

points = []
# Makes the initial feature class from the coordinates of the events stored in the catalog
for event in catalog:
    origin = event.preferred_origin()
    point = arcpy.Point(origin.longitude, origin.latitude)
    points.append(arcpy.PointGeometry(point))
arcpy.CopyFeatures_management(points, earthquakes)

# Adds useful fields to the output feature class
arcpy.AddField_management(earthquakes, "Describe", "STRING")
arcpy.AddField_management(earthquakes, "Magnitude", "Double")
arcpy.AddField_management(earthquakes, "Depth", "Double")
arcpy.AddField_management(earthquakes, "Time", "String")
eq_cursor = arcpy.da.UpdateCursor(earthquakes, ("Describe", "Magnitude", "Depth", "Time",))
for row, event in zip(eq_cursor, catalog):
    row[0] = event.short_str()
    row[1] = event.preferred_magnitude().mag
    row[2] = event.preferred_origin().depth
    row[3] = event.preferred_origin().time.format_iris_web_service()
    eq_cursor.updateRow(row)

# Adds the correct coordinate system to the output feature class
arcpy.DefineProjection_management(earthquakes, "wgs84.prj")
