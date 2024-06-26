"""
Function for converting 3D array of lat-long coordinates to projected coordinate system
"""

from osgeo import ogr
from osgeo import osr
from osgeo import gdal
import h5py as h5

gdal.UseExceptions()

def convert_latlong(lat:float,lon:float,refdata_path:str) -> tuple[float,float]:
    with gdal.Open(refdata_path) as ds:
        inSR = osr.SpatialReference()
        inSR.ImportFromWkt('GEOGCS["GCS_MOON", DATUM["D_MOON", SPHEROID["MOON",1737400,0]], PRIMEM["Reference_Meridian",0], UNIT["degree",0.0174532925199433, AUTHORITY["EPSG","9122"]]]')

        outSR = osr.SpatialReference()
        outSR.ImportFromWkt(ds.GetProjection())

        Point = ogr.Geometry(ogr.wkbPoint)
        Point.AddPoint(lon,lat)
        Point.AssignSpatialReference(inSR)
        Point.TransformTo(outSR)
        print(f"Transformation: Lat:{lat} Long:{lon}\n   --> X:{Point.GetX()} Y:{Point.GetY()}")


if __name__ == "__main__":
    with h5.File('Data/targeted.hdf5') as f:
        loc = f["Backplanes/LatLongElev"][:,:,:]

    #Formatted as (lat,long)
    pts = {
        "bl" : (loc[1,0,0],loc[0,0,0]),
        "tl" : (loc[1,-1,0],loc[0,-1,0]),
        "br" : (loc[1,0,-1],loc[0,0,-1]),
        "tr" : (loc[1,-1,-1],loc[0,-1,-1])
    }
    
    for key in pts.keys():
        print(key)
        convert_latlong(*pts[key],'C:/Lunar_Imagery_Data/MI_data/MI_MAP_03_N37E318N36E319SC.lbl')
