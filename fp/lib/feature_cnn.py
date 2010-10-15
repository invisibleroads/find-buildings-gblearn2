# Import system modules
import numpy
import itertools
# Import custom modules


# Core

class ConvolutionalNeuralNetworkFeatureSet(object):

    'Base class to generate an input window for a convolutional neural network'

    def extractFeatures(self, multispectralWindow, panchromaticWindow):
        return numpy.array(self.extractMatrices(multispectralWindow, panchromaticWindow))

class GrayscaleFeatureSet(ConvolutionalNeuralNetworkFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return panchromaticWindow.getMatrices()[0],

class FourStackedFeatureSet(ConvolutionalNeuralNetworkFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return multispectralWindow.getMatrices()

class FiveStackedFeatureSet(ConvolutionalNeuralNetworkFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        # Extract
        red, green, blue, infrared = multispectralWindow.getMatrices()
        panchromatic = panchromaticWindow.getMatrices()[0]
        # Draw
        redCanvas, greenCanvas, blueCanvas, infraredCanvas = [expandMatrixOnCanvas(x, panchromatic) for x in red, green, blue, infrared]
        # Return
        return redCanvas, greenCanvas, blueCanvas, infraredCanvas, panchromatic

class FiveCroppedFeatureSet(ConvolutionalNeuralNetworkFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        # Extract
        red, green, blue, infrared = multispectralWindow.getMatrices()
        panchromatic = centerCropMatrix(panchromaticWindow.getMatrices()[0], red.shape)
        # Return
        return red, green, blue, infrared, panchromatic

class YUVFiveStackedFeatureSet(ConvolutionalNeuralNetworkFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        # Extract
        red, green, blue, infrared = multispectralWindow.getMatrices()
        y, u, v = convertRGBToYUV(red, green, blue)
        panchromatic = panchromaticWindow.getMatrices()[0]
        # Draw
        yCanvas, uCanvas, vCanvas, infraredCanvas = [expandMatrixOnCanvas(x, panchromatic) for x in y, u, v, infrared]
        # Return
        return yCanvas, uCanvas, vCanvas, infraredCanvas, panchromatic

class SixStackedFeatureSet(FiveStackedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        # Extract
        redCanvas, greenCanvas, blueCanvas, infraredCanvas, panchromatic = super(SixStackedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow)
        infraredRedCanvas = infraredCanvas / (numpy.array(redCanvas, 'float') + 1)
        # Return
        return redCanvas, greenCanvas, blueCanvas, infraredCanvas, panchromatic, infraredRedCanvas

class NormalizedGrayscaleFeatureSet(GrayscaleFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return normalize(super(NormalizedGrayscaleFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class NormalizedFourStackedFeatureSet(FourStackedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return normalize(super(NormalizedFourStackedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class NormalizedFiveStackedFeatureSet(FiveStackedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return normalize(super(NormalizedFiveStackedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class NormalizedFiveCroppedFeatureSet(FiveCroppedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return normalize(super(NormalizedFiveCroppedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class NormalizedYUVFiveStackedFeatureSet(YUVFiveStackedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return normalize(super(NormalizedYUVFiveStackedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class NormalizedSixStackedFeatureSet(SixStackedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return normalize(super(NormalizedSixStackedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class FourStackedNormalizedFeatureSet(FourStackedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return map(normalize, super(FourStackedNormalizedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class FiveStackedNormalizedFeatureSet(FiveStackedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return map(normalize, super(FiveStackedNormalizedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

class FiveCroppedNormalizedFeatureSet(FiveCroppedFeatureSet):

    def extractMatrices(self, multispectralWindow, panchromaticWindow):
        return map(normalize, super(FiveCroppedNormalizedFeatureSet, self).extractMatrices(multispectralWindow, panchromaticWindow))

# Helpers

def normalize(matrix):
    matrix = numpy.array(matrix)
    return (matrix - numpy.mean(matrix)) / (1 + numpy.std(matrix))

def expandMatrixOnCanvas(subMatrix, superMatrix):
    # Measure
    subMatrixHeight, subMatrixWidth = subMatrix.shape
    superMatrixHeight, superMatrixWidth = superMatrix.shape
    heightRatio = superMatrixHeight / float(subMatrixHeight)
    widthRatio = superMatrixWidth / float(subMatrixWidth)
    # Overlay
    canvas = numpy.zeros(superMatrix.shape)
    for x in xrange(subMatrixWidth):
        for y in xrange(subMatrixHeight):
            left = int(x * widthRatio)
            right = int(x * widthRatio + widthRatio)
            top = int(y * heightRatio)
            bottom = int(y * heightRatio + heightRatio)
            window = numpy.ones((right - left, bottom - top)) * subMatrix[x, y]
            canvas[left : right, top : bottom] = window
    # Return
    return canvas

def centerMatrixOnCanvas(subMatrix, superMatrix):
    # Measure
    subMatrixHeight, subMatrixWidth = subMatrix.shape
    superMatrixHeight, superMatrixWidth = superMatrix.shape
    # Overlay
    canvas = numpy.zeros(superMatrix.shape)
    rowIndex = (superMatrixHeight - subMatrixHeight) / 2
    columnIndex = (superMatrixWidth - subMatrixWidth) / 2
    canvas[rowIndex : rowIndex + subMatrixHeight, columnIndex : columnIndex + subMatrixWidth] = subMatrix
    # Return
    return canvas

def centerCropMatrix(matrix, centerDimensions):
    centerWidth, centerHeight = centerDimensions
    matrixWidth, matrixHeight = matrix.shape
    xOffset = (matrixWidth - centerWidth) / 2
    yOffset = (matrixHeight - centerHeight) / 2
    return matrix[xOffset : xOffset + centerWidth, yOffset : yOffset + centerHeight]

def convertRGBToYUV(red, green, blue):
    # Initialize
    ys = []; us = []; vs = []
    shape = red.shape
    matrix = numpy.array([[0.299, 0.587, 0.114], [-0.14713, -0.28886, 0.436], [0.615, -0.51499, -0.10001]])
    # For each value,
    for rgb in itertools.izip(red.flat, green.flat, blue.flat):
        y, u, v = numpy.dot(matrix, rgb)
        ys.append(y)
        us.append(u)
        vs.append(v)
    # Return
    return numpy.array(ys).reshape(shape), numpy.array(us).reshape(shape), numpy.array(vs).reshape(shape)
