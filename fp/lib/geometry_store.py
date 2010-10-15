# Import system modules
import osgeo.ogr
import osgeo.osr
import re
import os
# Import custom modules
import store


# Set
pattern_geometryName = re.compile(r'([^(]*)')
extensionByName = {
    'ESRI Shapefile': 'shp',
}
typeByName = {
    'POINT': osgeo.ogr.wkbPoint,
    'LINESTRING': osgeo.ogr.wkbLineString,
    'POLYGON': osgeo.ogr.wkbPolygon,
}


def save(targetPath, wktGeometries, spatialReferenceAsProj4, driverName='ESRI Shapefile'):
    # Get driver
    driver = osgeo.ogr.GetDriverByName(driverName)
    # Create data
    targetPath = store.replaceFileExtension(targetPath, extensionByName[driverName])
    if os.path.exists(targetPath): 
        os.remove(targetPath)
    dataSource = driver.CreateDataSource(targetPath)
    # If wktGeometries is empty, return
    if not wktGeometries: 
        return targetPath
    # Create spatialReference
    spatialReference = osgeo.osr.SpatialReference()
    spatialReference.ImportFromProj4(spatialReferenceAsProj4)
    # Create layer
    geometryName = pattern_geometryName.match(wktGeometries[0]).group(1).strip()
    geometryType = typeByName[geometryName]
    layerName = store.extractFileBaseName(targetPath)
    layer = dataSource.CreateLayer(layerName, spatialReference, geometryType)
    layerDefinition = layer.GetLayerDefn()
    # For each geometry,
    for featureIndex, wktGeometry in enumerate(wktGeometries):
        # Create geometry
        geometry = osgeo.ogr.CreateGeometryFromWkt(wktGeometry)
        # Create feature
        feature = osgeo.ogr.Feature(layerDefinition)
        feature.SetGeometry(geometry)
        feature.SetFID(featureIndex)
        # Save feature
        layer.CreateFeature(feature)
    # Return
    return targetPath


def load(sourcePath, driverName='ESRI Shapefile'):
    # Open
    sourcePath = store.replaceFileExtension(sourcePath, extensionByName[driverName])
    dataSource = osgeo.ogr.Open(sourcePath)
    # Get the first layer
    layer = dataSource.GetLayer()
    # Initialize
    wktGeometries = []
    # For each point,
    for index in xrange(layer.GetFeatureCount()):
        # Get feature
        feature = layer.GetFeature(index)
        # Get geometry
        geometry = feature.GetGeometryRef()
        # Append
        wktGeometries.append(geometry.ExportToWkt())
    # Return
    return wktGeometries, layer.GetSpatialRef().ExportToProj4()
