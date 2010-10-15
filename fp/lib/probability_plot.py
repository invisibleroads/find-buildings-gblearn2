# Import system modules
import Image
import numpy
import itertools
# Import custom modules
import probability_store
import point_store
import store


def plot(targetImagePath, points, probabilities):
    # Load
    normalizedProbabilities = normalize(probabilities)
    probabilityByXY = dict(itertools.izip(points, normalizedProbabilities))
    # Initialize color
    maximumColor = numpy.array([255, 255, 255])
    # Initialize image
    xs = list(set([x[0] for x in points])); xs.sort()
    ys = list(set([x[1] for x in points])); xs.sort()
    imageWidth = len(xs)
    imageHeight = len(ys)
    image = Image.new('RGB', (imageWidth, imageHeight))
    pixels = image.load()
    # Fill image
    for xIndex in xrange(len(xs)):
        for yIndex in xrange(len(ys)):
            xy = xs[xIndex], ys[yIndex]
            colorFraction = probabilityByXY[xy] if xy in probabilityByXY else 0
            pixels[xIndex, yIndex] = tuple(map(int, maximumColor * colorFraction))
    # Save matrix as an image
    targetImagePath = store.replaceFileExtension(targetImagePath, 'png')
    image.save(targetImagePath)
    return targetImagePath


def normalize(numbers):
    numbers = numpy.array(numbers)
    shiftedNumbers = numbers - min(numbers)
    return shiftedNumbers / float(max(abs(shiftedNumbers)))
