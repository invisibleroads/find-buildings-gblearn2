# Import system modules
# import scipy.cluster.vq
import Pycluster
import numpy
# Import custom modules
import view
import point_store, point_process
import image_store
import probability_store


# Define core

def cluster(targetLocationPath, probabilityPath, iterationCountPerBurst, maximumGeoDiameter, minimumGeoDiameter):
    # Initialize
    probabilityInformation = probability_store.Information(probabilityPath)
    imagePath = probabilityInformation.getImagePath()
    imageInformation = image_store.Information(imagePath)
    multispectralImage = imageInformation.getMultispectralImage()
    multispectralGeoTransform = multispectralImage.getGeoTransform()
    spatialReference = multispectralImage.getSpatialReference()
    # Convert maximumGeoDiameter into maximumPixelDiameter
    maximumPixelDiameter = max(image_store.convertGeoDimensionsToPixelDimensions(maximumGeoDiameter, maximumGeoDiameter, multispectralGeoTransform))
    # Convert minimumGeoDiameter into minimumPixelDiameter
    minimumPixelDiameter = max(image_store.convertGeoDimensionsToPixelDimensions(minimumGeoDiameter, minimumGeoDiameter, multispectralGeoTransform))
    # Load pixelDimensions
    windowGeoLength = probabilityInformation.getWindowLengthInMeters()
    pixelWidth, pixelHeight = image_store.convertGeoDimensionsToPixelDimensions(windowGeoLength, windowGeoLength, multispectralGeoTransform)
    # Cluster
    probabilityPacks = probability_store.load(probabilityPath)
    vectors = [(x, y, probability) for x, y, label, probability in probabilityPacks if label == 1]
    windowLocations = grapeCluster(vectors, iterationCountPerBurst, maximumPixelDiameter, minimumPixelDiameter)
    windowCenters = [(xy[0] + pixelWidth / 2, xy[1] + pixelHeight / 2) for xy in windowLocations]
    geoCenters = image_store.convertPixelLocationsToGeoLocations(windowCenters, multispectralGeoTransform)
    # Save
    point_store.save(targetLocationPath, geoCenters, spatialReference)


# Define helpers

def grapeCluster(vectors, iterationCountPerBurst, maximumPixelDiameter, minimumPixelDiameter):
    # If we have no vectors, return empty array
    if not vectors: return []
    # Assign all vectors to a single cluster
    globalClusters = [numpy.array(vectors)]
    globalCount = len(vectors)
    globalClusterMeans = []
    # While there are globalClusters,
    while globalClusters:
        # Pop the last cluster
        globalCluster = globalClusters.pop()
        # Measure size
        sizeCategory = measureClusterSize(globalCluster, maximumPixelDiameter, minimumPixelDiameter)
        # If it is too big,
        if sizeCategory > 0:
            # Burst it
            # assignments = scipy.cluster.vq.kmeans2(globalCluster, k=2, iter=iterationCountPerBurst)[1]
            assignments = Pycluster.kcluster(globalCluster, npass=iterationCountPerBurst)[0]
            # Extract localClusters
            booleanAssignments = numpy.array(assignments) > 0
            localClusters = globalCluster[booleanAssignments], globalCluster[~booleanAssignments]
            # Push localClusters to the end of the stack
            globalClusters.extend(localClusters)
        # If it is the right size, append the weighted mean
        elif sizeCategory == 0: 
            globalClusterMeans.append(computeWeightedMean(globalCluster))
        # Show feedback
        view.printPercentUpdate(globalCount - len(globalClusters), globalCount)
    # Return
    view.printPercentFinal(globalCount)
    return globalClusterMeans


def measureClusterSize(cluster, maximumPixelDiameter, minimumPixelDiameter):
    # Initialize
    clusterDiameter = 0
    # For each point in the cluster,
    for index in xrange(len(cluster)):
        # Get fromPoint
        fromPoint = cluster[index]
        # For each other point in the cluster,
        for toPoint in cluster[index + 1:]:
            # Compute pairwiseDistance
            innerDistance = point_process.computeDistance(fromPoint, toPoint)
            # Check if it is too big
            if innerDistance > maximumPixelDiameter: 
                return 1
            # Save clusterDiameter
            clusterDiameter = innerDistance if innerDistance > clusterDiameter else clusterDiameter
    # Check if it is too small
    if clusterDiameter < minimumPixelDiameter:
        return -1
    # It is the right size
    return 0


def computeWeightedMean(cluster):
    xs = numpy.array([point[0] for point in cluster])
    ys = numpy.array([point[1] for point in cluster])
    probabilities = numpy.array([point[2] for point in cluster])
    return numpy.array([numpy.dot(xs, probabilities), numpy.dot(ys, probabilities)]) / float(sum(probabilities))
