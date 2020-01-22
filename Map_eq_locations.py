# for mapping events from the obspy catalog file into arcGIS
from obspy import read_events
import arcpy
earthquakes = arcpy.GetParameter(0)
catalog = read_events("C:/Users/messertoby/PycharmProjects/Match-filter-detection/catalog")
points = []
for event in catalog:
    origin = event.preferred_origin()
    point = arcpy.Point(origin.latitude, origin.longitude)
    points.append(arcpy.PointGeometry(point))

arcpy.CopyFeatures_management(points,earthquakes)
arcpy.AddField_management(earthquakes, "Describe", "STRING")
eq_cursor = arcpy.da.UpdateCursor(earthquakes, ("Describe",))

for row, event in zip(eq_cursor, catalog):
    row[0] = event.short_str()
    eq_cursor.updateRow(row)