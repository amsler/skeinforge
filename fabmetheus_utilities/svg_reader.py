"""
Svg reader.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.solids import trianglemesh
from fabmetheus_utilities.xml_simple_reader import XMLSimpleReader
from fabmetheus_utilities import archive
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
from fabmetheus_utilities import settings
from fabmetheus_utilities import svg_writer
import math
import os
import sys
import traceback


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


globalNumberOfCornerPoints = 11
globalNumberOfBezierPoints = globalNumberOfCornerPoints + globalNumberOfCornerPoints
globalNumberOfCirclePoints = 4 * globalNumberOfCornerPoints


def addFunctionsToDictionary( dictionary, functions, prefix ):
	"Add functions to dictionary."
	for function in functions:
		dictionary[ function.__name__[ len( prefix ) : ] ] = function

def getArcComplexes(begin, end, largeArcFlag, radius, sweepFlag, xAxisRotation):
	'Get the arc complexes, procedure at http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes'
	xAxisRotationComplex = euclidean.getWiddershinsUnitPolar(xAxisRotation)
	reverseXAxisRotationComplex = complex(xAxisRotationComplex.real, -xAxisRotationComplex.imag)
	beginRotated = begin * reverseXAxisRotationComplex
	beginTransformed = complex(beginRotated.real / radius.real, beginRotated.imag / radius.imag)
	endRotated = end * reverseXAxisRotationComplex
	endTransformed = complex(endRotated.real / radius.real, endRotated.imag / radius.imag)
	midpointTransformed = 0.5 * (beginTransformed + endTransformed)
	midMinusBeginTransformed = midpointTransformed - beginTransformed
	midMinusBeginTransformedLength = abs(midMinusBeginTransformed)
	midWiddershinsTransformed = complex(-midMinusBeginTransformed.imag, midMinusBeginTransformed.real)
	midWiddershinsLengthSquared = 1.0 - midMinusBeginTransformedLength * midMinusBeginTransformedLength
	if midWiddershinsLengthSquared < 0.0:
		print('Warning, the radius is too small for getArcComplexes in svgReader')
		print(begin)
		print(end)
		print(radius)
		return []
	midWiddershinsLength = midWiddershinsLengthSquared
	midWiddershinsTransformed *= midWiddershinsLength / abs(midWiddershinsTransformed)
	centerTransformed = midpointTransformed
	if largeArcFlag == sweepFlag:
		centerTransformed -= midWiddershinsTransformed
	else:
		centerTransformed += midWiddershinsTransformed
	beginMinusCenterTransformed = beginTransformed - centerTransformed
	beginMinusCenterTransformedLength = abs(beginMinusCenterTransformed)
	if beginMinusCenterTransformedLength <= 0.0:
		return end
	beginAngle = math.atan2(beginMinusCenterTransformed.imag, beginMinusCenterTransformed.real)
	endMinusCenterTransformed = endTransformed - centerTransformed
	angleDifference = euclidean.getAngleDifferenceByComplex(endMinusCenterTransformed, beginMinusCenterTransformed)
	if sweepFlag:
		if angleDifference < 0.0:
			angleDifference += 2.0 * math.pi
	else:
		if angleDifference > 0.0:
			angleDifference -= 2.0 * math.pi
	global globalSideAngle
	sides = int(math.ceil(abs(angleDifference) / globalSideAngle))
	sideAngle = angleDifference / float(sides)
	arcComplexes = []
	center = complex(centerTransformed.real * radius.real, centerTransformed.imag * radius.imag) * xAxisRotationComplex
	for side in xrange(1, sides):
		unitPolar = euclidean.getWiddershinsUnitPolar(beginAngle + float(side) * sideAngle)
		circumferential = complex(unitPolar.real * radius.real, unitPolar.imag * radius.imag) * beginMinusCenterTransformedLength
		point = center + circumferential * xAxisRotationComplex
		arcComplexes.append(point)
	arcComplexes.append(end)
	return arcComplexes

def getChainMatrixSVG(matrixSVG, xmlElement):
	"Get chain matrixSVG by svgElement."
	matrixSVG = matrixSVG.getOtherTimesSelf(getMatrixSVG(xmlElement).tricomplex)
	if xmlElement.parent != None:
		matrixSVG = getChainMatrixSVG(matrixSVG, xmlElement.parent)
	return matrixSVG

def getChainMatrixSVGIfNecessary(xmlElement, yAxisPointingUpward):
	"Get chain matrixSVG by svgElement and yAxisPointingUpward."
	matrixSVG = MatrixSVG()
	if yAxisPointingUpward:
		return matrixSVG
	return getChainMatrixSVG(matrixSVG, xmlElement)

def getCubicPoint( along, begin, controlPoints, end ):
	'Get the cubic point.'
	segmentBegin = getQuadraticPoint( along, begin, controlPoints[0], controlPoints[1] )
	segmentEnd = getQuadraticPoint( along, controlPoints[0], controlPoints[1], end )
	return ( 1.0 - along ) * segmentBegin + along * segmentEnd

def getCubicPoints( begin, controlPoints, end, numberOfBezierPoints=globalNumberOfBezierPoints):
	'Get the cubic points.'
	bezierPortion = 1.0 / float(numberOfBezierPoints)
	cubicPoints = []
	for bezierIndex in xrange( 1, numberOfBezierPoints + 1 ):
		cubicPoints.append(getCubicPoint(bezierPortion * bezierIndex, begin, controlPoints, end))
	return cubicPoints

def getFontReader(fontFamily):
	"Get the font reader for the fontFamily."
	fontLower = fontFamily.lower().replace(' ', '_')
	global globalFontReaderDictionary
	if fontLower in globalFontReaderDictionary:
		return globalFontReaderDictionary[fontLower]
	global globalFontFileNames
	if globalFontFileNames == None:
		globalFontFileNames = gcodec.getPluginFileNamesFromDirectoryPath(getFontsDirectoryPath())
	if fontLower not in globalFontFileNames:
		print('Warning, the %s font was not found in the fonts folder, so Gentium Basic Regular will be substituted.' % fontFamily)
		fontLower = 'gentium_basic_regular'
	fontReader = FontReader(fontLower)
	globalFontReaderDictionary[fontLower] = fontReader
	return fontReader

def getFontsDirectoryPath():
	"Get the fonts directory path."
	return archive.getFabmetheusUtilitiesPath('fonts')

def getLabelString(dictionary):
	"Get the label string for the dictionary."
	for key in dictionary:
		labelIndex = key.find('label')
		if labelIndex >= 0:
			return dictionary[key]
	return ''

def getMatrixSVG(xmlElement):
	"Get matrixSVG by svgElement."
	matrixSVG = MatrixSVG()
	if 'transform' not in xmlElement.attributeDictionary:
		return matrixSVG
	transformWords = []
	for transformWord in xmlElement.attributeDictionary['transform'].replace(')', '(').split('('):
		transformWordStrip = transformWord.strip()
		if transformWordStrip != '': # workaround for split(character) bug which leaves an extra empty element
			transformWords.append(transformWordStrip)
	global globalGetTricomplexDictionary
	getTricomplexDictionaryKeys = globalGetTricomplexDictionary.keys()
	for transformWordIndex, transformWord in enumerate(transformWords):
		if transformWord in getTricomplexDictionaryKeys:
			transformString = transformWords[transformWordIndex + 1].replace(',', ' ')
			matrixSVG = matrixSVG.getSelfTimesOther(globalGetTricomplexDictionary[ transformWord ](transformString.split()))
	return matrixSVG

def getQuadraticPoint( along, begin, controlPoint, end ):
	'Get the quadratic point.'
	oneMinusAlong = 1.0 - along
	segmentBegin = oneMinusAlong * begin + along * controlPoint
	segmentEnd = oneMinusAlong * controlPoint + along * end
	return oneMinusAlong * segmentBegin + along * segmentEnd

def getQuadraticPoints(begin, controlPoint, end, numberOfBezierPoints=globalNumberOfBezierPoints):
	'Get the quadratic points.'
	bezierPortion = 1.0 / float(numberOfBezierPoints)
	quadraticPoints = []
	for bezierIndex in xrange(1, numberOfBezierPoints + 1):
		quadraticPoints.append(getQuadraticPoint(bezierPortion * bezierIndex, begin, controlPoint, end))
	return quadraticPoints

def getRightStripAlphabetPercent(word):
	"Get word with alphabet characters and the percent sign stripped from the right."
	word = word.strip()
	for characterIndex in xrange(len(word) - 1, -1, -1):
		character = word[characterIndex]
		if not character.isalpha() and not character == '%':
			return float(word[: characterIndex + 1])
	return None

def getRightStripMinusSplit(lineString):
	"Get string with spaces after the minus sign stripped."
	oldLineStringLength = -1
	while oldLineStringLength < len(lineString):
		oldLineStringLength = len(lineString)
		lineString = lineString.replace('- ', '-')
	return lineString.split()

def getStrokeRadius(xmlElement):
	"Get the stroke radius."
	return 0.5 * getRightStripAlphabetPercent(getStyleValue('1.0', 'stroke-width', xmlElement))

def getStyleValue(defaultValue, key, xmlElement):
	"Get the stroke value string."
	if 'style' in xmlElement.attributeDictionary:
		line = xmlElement.attributeDictionary['style']
		strokeIndex = line.find(key)
		if strokeIndex > -1:
			words = line[strokeIndex :].replace(':', ' ').replace(';', ' ').split()
			if len(words) > 1:
				return words[1]
	if key in xmlElement.attributeDictionary:
		return xmlElement.attributeDictionary[key]
	if xmlElement.parent == None:
		return defaultValue
	return getStyleValue(defaultValue, key, xmlElement.parent)

def getTextComplexLoops(fontFamily, fontSize, text, yAxisPointingUpward=True):
	"Get text as complex loops."
	textComplexLoops = []
	fontReader = getFontReader(fontFamily)
	horizontalAdvanceX = 0.0
	for character in text:
		glyph = fontReader.getGlyph(character, yAxisPointingUpward)
		textComplexLoops += glyph.getSizedAdvancedLoops(fontSize, horizontalAdvanceX, yAxisPointingUpward)
		horizontalAdvanceX += glyph.horizontalAdvanceX
	return textComplexLoops

def getTransformedFillOutline(loop, xmlElement, yAxisPointingUpward):
	"Get the loops if fill is on, otherwise get the outlines."
	fillOutlineLoops = None
	if getStyleValue('none', 'fill', xmlElement).lower() == 'none':
		fillOutlineLoops = intercircle.getAroundsFromLoop(loop, getStrokeRadius(xmlElement))
	else:
		fillOutlineLoops = [loop]
	return getChainMatrixSVGIfNecessary(xmlElement, yAxisPointingUpward).getTransformedPaths(fillOutlineLoops)

def getTransformedOutlineByPath(path, xmlElement, yAxisPointingUpward):
	"Get the outline from the path."
	aroundsFromPath = intercircle.getAroundsFromPath(path, getStrokeRadius(xmlElement))
	return getChainMatrixSVGIfNecessary(xmlElement, yAxisPointingUpward).getTransformedPaths(aroundsFromPath)

def getTransformedOutlineByPaths(paths, xmlElement, yAxisPointingUpward):
	"Get the outline from the paths."
	aroundsFromPaths = intercircle.getAroundsFromPaths(paths, getStrokeRadius(xmlElement))
	return getChainMatrixSVGIfNecessary(xmlElement, yAxisPointingUpward).getTransformedPaths(aroundsFromPaths)

def getTricomplexmatrix(transformWords):
	"Get matrixSVG by transformWords."
	tricomplex = [euclidean.getComplexByWords(transformWords)]
	tricomplex.append(euclidean.getComplexByWords(transformWords, 2))
	tricomplex.append(euclidean.getComplexByWords(transformWords, 4))
	return tricomplex

def getTricomplexrotate(transformWords):
	"Get matrixSVG by transformWords."
	rotate = euclidean.getWiddershinsUnitPolar(math.radians(float(transformWords[0])))
	return [rotate, complex(-rotate.imag,rotate.real), complex()]

def getTricomplexscale(transformWords):
	"Get matrixSVG by transformWords."
	scale = euclidean.getComplexByWords(transformWords)
	return [complex(scale.real,0.0), complex(0.0,scale.imag), complex()]

def getTricomplexskewX(transformWords):
	"Get matrixSVG by transformWords."
	skewX = math.tan(math.radians(float(transformWords[0])))
	return [complex(1.0, 0.0), complex(skewX, 1.0), complex()]

def getTricomplexskewY(transformWords):
	"Get matrixSVG by transformWords."
	skewY = math.tan(math.radians(float(transformWords[0])))
	return [complex(1.0, skewY), complex(0.0, 1.0), complex()]

def getTricomplexTimesColumn(firstTricomplex, otherColumn):
	"Get this matrix multiplied by the otherColumn."
	dotProductX = firstTricomplex[0].real * otherColumn.real + firstTricomplex[1].real * otherColumn.imag
	dotProductY = firstTricomplex[0].imag * otherColumn.real + firstTricomplex[1].imag * otherColumn.imag
	return complex(dotProductX, dotProductY)

def getTricomplexTimesOther(firstTricomplex, otherTricomplex):
	"Get the first tricomplex multiplied by the other tricomplex."
	#A down, B right from http://en.wikipedia.org/wiki/Matrix_multiplication
	tricomplexTimesOther = [getTricomplexTimesColumn(firstTricomplex, otherTricomplex[0])]
	tricomplexTimesOther.append(getTricomplexTimesColumn(firstTricomplex, otherTricomplex[1]))
	tricomplexTimesOther.append(getTricomplexTimesColumn(firstTricomplex, otherTricomplex[2]) + firstTricomplex[2])
	return tricomplexTimesOther

def getTricomplextranslate(transformWords):
	"Get matrixSVG by transformWords."
	translate = euclidean.getComplexByWords(transformWords)
	return [complex(1.0, 0.0), complex(0.0, 1.0), translate]

def processSVGElementcircle( svgReader, xmlElement ):
	"Process xmlElement by svgReader."
	attributeDictionary = xmlElement.attributeDictionary
	center = euclidean.getComplexDefaultByDictionaryKeys( complex(), attributeDictionary, 'cx', 'cy')
	radius = euclidean.getFloatDefaultByDictionary( 0.0, attributeDictionary, 'r')
	if radius == 0.0:
		print('Warning, in processSVGElementcircle in svgReader radius is zero in:')
		print(attributeDictionary)
		return
	global globalNumberOfCirclePoints
	global globalSideAngle
	loop = []
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	for side in xrange( globalNumberOfCirclePoints ):
		unitPolar = euclidean.getWiddershinsUnitPolar( float(side) * globalSideAngle )
		loop.append( center + radius * unitPolar )
	rotatedLoopLayer.loops += getTransformedFillOutline(loop, xmlElement, svgReader.yAxisPointingUpward)

def processSVGElementellipse( svgReader, xmlElement ):
	"Process xmlElement by svgReader."
	attributeDictionary = xmlElement.attributeDictionary
	center = euclidean.getComplexDefaultByDictionaryKeys( complex(), attributeDictionary, 'cx', 'cy')
	radius = euclidean.getComplexDefaultByDictionaryKeys( complex(), attributeDictionary, 'rx', 'ry')
	if radius.real == 0.0 or radius.imag == 0.0:
		print('Warning, in processSVGElementellipse in svgReader radius is zero in:')
		print(attributeDictionary)
		return
	global globalNumberOfCirclePoints
	global globalSideAngle
	loop = []
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	for side in xrange( globalNumberOfCirclePoints ):
		unitPolar = euclidean.getWiddershinsUnitPolar( float(side) * globalSideAngle )
		loop.append( center + complex( unitPolar.real * radius.real, unitPolar.imag * radius.imag ) )
	rotatedLoopLayer.loops += getTransformedFillOutline(loop, xmlElement, svgReader.yAxisPointingUpward)

def processSVGElementg( svgReader, xmlElement ):
	"Process xmlElement by svgReader."
	if 'id' not in xmlElement.attributeDictionary:
		return
	idString = xmlElement.attributeDictionary['id'].lower()
	if idString == 'beginningofcontrolsection':
		svgReader.stopProcessing = True
		return
	zIndex = idString.find('z:')
	if zIndex < 0:
		idString = getLabelString(xmlElement.attributeDictionary)
		zIndex = idString.find('z:')
	if zIndex < 0:
		return
	floatFromValue = euclidean.getFloatFromValue( idString[ zIndex + len('z:') : ].strip() )
	if floatFromValue != None:
		svgReader.z = floatFromValue
	svgReader.bridgeRotation = euclidean.getComplexDefaultByDictionary( None, xmlElement.attributeDictionary, 'bridgeRotation')

def processSVGElementline(svgReader, xmlElement):
	"Process xmlElement by svgReader."
	begin = euclidean.getComplexDefaultByDictionaryKeys(complex(), xmlElement.attributeDictionary, 'x1', 'y1')
	end = euclidean.getComplexDefaultByDictionaryKeys(complex(), xmlElement.attributeDictionary, 'x2', 'y2')
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	rotatedLoopLayer.loops += getTransformedOutlineByPath([begin, end], xmlElement, svgReader.yAxisPointingUpward)

def processSVGElementpath( svgReader, xmlElement ):
	"Process xmlElement by svgReader."
	if 'd' not in xmlElement.attributeDictionary:
		print('Warning, in processSVGElementpath in svgReader can not get a value for d in:')
		print(xmlElement.attributeDictionary)
		return
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	PathReader(rotatedLoopLayer.loops, xmlElement, svgReader.yAxisPointingUpward)

def processSVGElementpolygon( svgReader, xmlElement ):
	"Process xmlElement by svgReader."
	if 'points' not in xmlElement.attributeDictionary:
		print('Warning, in processSVGElementpolygon in svgReader can not get a value for d in:')
		print(xmlElement.attributeDictionary)
		return
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	words = getRightStripMinusSplit(xmlElement.attributeDictionary['points'].replace(',', ' '))
	loop = []
	for wordIndex in xrange( 0, len(words), 2 ):
		loop.append(euclidean.getComplexByWords(words[wordIndex :]))
	rotatedLoopLayer.loops += getTransformedFillOutline(loop, xmlElement, svgReader.yAxisPointingUpward)

def processSVGElementpolyline(svgReader, xmlElement):
	"Process xmlElement by svgReader."
	if 'points' not in xmlElement.attributeDictionary:
		print('Warning, in processSVGElementpolyline in svgReader can not get a value for d in:')
		print(xmlElement.attributeDictionary)
		return
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	words = getRightStripMinusSplit(xmlElement.attributeDictionary['points'].replace(',', ' '))
	path = []
	for wordIndex in xrange(0, len(words), 2):
		path.append(euclidean.getComplexByWords(words[wordIndex :]))
	rotatedLoopLayer.loops += getTransformedOutlineByPath(path, xmlElement, svgReader.yAxisPointingUpward)

def processSVGElementrect( svgReader, xmlElement ):
	"Process xmlElement by svgReader."
	attributeDictionary = xmlElement.attributeDictionary
	height = euclidean.getFloatDefaultByDictionary( 0.0, attributeDictionary, 'height')
	if height == 0.0:
		print('Warning, in processSVGElementrect in svgReader height is zero in:')
		print(attributeDictionary)
		return
	width = euclidean.getFloatDefaultByDictionary( 0.0, attributeDictionary, 'width')
	if width == 0.0:
		print('Warning, in processSVGElementrect in svgReader width is zero in:')
		print(attributeDictionary)
		return
	center = euclidean.getComplexDefaultByDictionaryKeys(complex(), attributeDictionary, 'x', 'y')
	inradius = 0.5 * complex( width, height )
	cornerRadius = euclidean.getComplexDefaultByDictionaryKeys( complex(), attributeDictionary, 'rx', 'ry')
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	if cornerRadius.real == 0.0 and cornerRadius.imag == 0.0:
		inradiusMinusX = complex( - inradius.real, inradius.imag )
		loop = [center + inradius, center + inradiusMinusX, center - inradius, center - inradiusMinusX]
		rotatedLoopLayer.loops += getTransformedFillOutline(loop, xmlElement, svgReader.yAxisPointingUpward)
		return
	if cornerRadius.real == 0.0:
		cornerRadius = complex( cornerRadius.imag, cornerRadius.imag )
	elif cornerRadius.imag == 0.0:
		cornerRadius = complex( cornerRadius.real, cornerRadius.real )
	cornerRadius = complex( min( cornerRadius.real, inradius.real ), min( cornerRadius.imag, inradius.imag ) )
	ellipsePath = [ complex( cornerRadius.real, 0.0 ) ]
	inradiusMinusCorner = inradius - cornerRadius
	loop = []
	global globalNumberOfCornerPoints
	global globalSideAngle
	for side in xrange( 1, globalNumberOfCornerPoints ):
		unitPolar = euclidean.getWiddershinsUnitPolar( float(side) * globalSideAngle )
		ellipsePath.append( complex( unitPolar.real * cornerRadius.real, unitPolar.imag * cornerRadius.imag ) )
	ellipsePath.append( complex( 0.0, cornerRadius.imag ) )
	cornerPoints = []
	for point in ellipsePath:
		cornerPoints.append( point + inradiusMinusCorner )
	cornerPointsReversed = cornerPoints[: : -1]
	for cornerPoint in cornerPoints:
		loop.append( center + cornerPoint )
	for cornerPoint in cornerPointsReversed:
		loop.append( center + complex( - cornerPoint.real, cornerPoint.imag ) )
	for cornerPoint in cornerPoints:
		loop.append( center - cornerPoint )
	for cornerPoint in cornerPointsReversed:
		loop.append( center + complex( cornerPoint.real, - cornerPoint.imag ) )
	loop = euclidean.getLoopWithoutCloseSequentialPoints( 0.0001 * abs(inradius), loop )
	rotatedLoopLayer.loops += getTransformedFillOutline(loop, xmlElement, svgReader.yAxisPointingUpward)

def processSVGElementtext(svgReader, xmlElement):
	"Process xmlElement by svgReader."
	if svgReader.yAxisPointingUpward:
		return
	fontFamily = getStyleValue('Gentium Basic Regular', 'font-family', xmlElement)
	fontSize = getRightStripAlphabetPercent(getStyleValue('12.0', 'font-size', xmlElement))
	matrixSVG = getChainMatrixSVGIfNecessary(xmlElement, svgReader.yAxisPointingUpward)
	rotatedLoopLayer = svgReader.getRotatedLoopLayer()
	translate = euclidean.getComplexDefaultByDictionaryKeys(complex(), xmlElement.attributeDictionary, 'x', 'y')
	for textComplexLoop in getTextComplexLoops(fontFamily, fontSize, xmlElement.text, svgReader.yAxisPointingUpward):
		translatedLoop = []
		for textComplexPoint in textComplexLoop:
			translatedLoop.append(textComplexPoint + translate )
		rotatedLoopLayer.loops.append(matrixSVG.getTransformedPath(translatedLoop))


class FontReader:
	"Class to read a font in the fonts folder."
	def __init__(self, fontFamily):
		"Initialize."
		self.fontFamily = fontFamily
		self.glyphDictionary = {}
		self.glyphXMLElementDictionary = {}
		self.missingGlyph = None
		fileName = os.path.join(getFontsDirectoryPath(), fontFamily + '.svg')
		self.xmlParser = XMLSimpleReader(fileName, None, gcodec.getFileText(fileName))
		self.fontXMLElement = self.xmlParser.getRoot().getFirstChildWithClassName('defs').getFirstChildWithClassName('font')
		self.fontFaceXMLElement = self.fontXMLElement.getFirstChildWithClassName('font-face')
		self.unitsPerEM = float(self.fontFaceXMLElement.attributeDictionary['units-per-em'])
		glyphXMLElements = self.fontXMLElement.getChildrenWithClassName('glyph')
		for glyphXMLElement in glyphXMLElements:
			self.glyphXMLElementDictionary[glyphXMLElement.attributeDictionary['unicode']] = glyphXMLElement

	def getGlyph(self, character, yAxisPointingUpward):
		"Get the glyph for the character."
		if character not in self.glyphXMLElementDictionary:
			if self.missingGlyph == None:
				missingGlyphXMLElement = self.fontXMLElement.getFirstChildWithClassName('missing-glyph')
				self.missingGlyph = Glyph(self.unitsPerEM, missingGlyphXMLElement, yAxisPointingUpward)
			return self.missingGlyph
		if character not in self.glyphDictionary:
			self.glyphDictionary[character] = Glyph(self.unitsPerEM, self.glyphXMLElementDictionary[character], yAxisPointingUpward)
		return self.glyphDictionary[character]


class Glyph:
	"Class to handle a glyph."
	def __init__(self, unitsPerEM, xmlElement, yAxisPointingUpward):
		"Initialize."
		self.horizontalAdvanceX = float(xmlElement.attributeDictionary['horiz-adv-x'])
		self.loops = []
		self.unitsPerEM = unitsPerEM
		xmlElement.attributeDictionary['fill'] = ''
		if 'd' not in xmlElement.attributeDictionary:
			return
		PathReader(self.loops, xmlElement, yAxisPointingUpward)

	def getSizedAdvancedLoops(self, fontSize, horizontalAdvanceX, yAxisPointingUpward=True):
		"Get loops for font size, advanced horizontally."
		multiplierX = fontSize / self.unitsPerEM
		multiplierY = multiplierX
		if not yAxisPointingUpward:
			multiplierY = -multiplierY
		sizedLoops = []
		for loop in self.loops:
			sizedLoop = []
			sizedLoops.append(sizedLoop)
			for point in loop:
				sizedLoop.append( complex(multiplierX * (point.real + horizontalAdvanceX), multiplierY * point.imag))
		return sizedLoops


class MatrixSVG:
	"Two by three svg matrix."
	def __init__(self, tricomplex=None):
		"Initialize."
		self.tricomplex = tricomplex

	def __repr__(self):
		"Get the string representation of this two by three svg matrix."
		return str(self.tricomplex)

	def getOtherTimesSelf(self, otherTricomplex):
		"Get the other matrix multiplied by this matrix."
		if otherTricomplex == None:
			return MatrixSVG(self.tricomplex)
		if self.tricomplex == None:
			return MatrixSVG(otherTricomplex)
		return MatrixSVG(getTricomplexTimesOther(otherTricomplex, self.tricomplex))

	def getSelfTimesOther(self, otherTricomplex):
		"Get this matrix multiplied by the other matrix."
		if otherTricomplex == None:
			return MatrixSVG(self.tricomplex)
		if self.tricomplex == None:
			return MatrixSVG(otherTricomplex)
		return MatrixSVG(getTricomplexTimesOther(self.tricomplex, otherTricomplex))

	def getTransformedPath(self, path):
		"Get transformed path."
		if self.tricomplex == None:
			return path
		complexX = self.tricomplex[0]
		complexY = self.tricomplex[1]
		complexTranslation = self.tricomplex[2]
		transformedPath = []
		for point in path:
			x = complexX.real * point.real + complexY.real * point.imag
			y = complexX.imag * point.real + complexY.imag * point.imag
			transformedPath.append(complex(x, y) + complexTranslation)
		return transformedPath

	def getTransformedPaths(self, paths):
		"Get transformed paths."
		if self.tricomplex == None:
			return paths
		transformedPaths = []
		for path in paths:
			transformedPaths.append(self.getTransformedPath(path))
		return transformedPaths


class PathReader:
	"Class to read svg path."
	def __init__(self, loops, xmlElement, yAxisPointingUpward):
		"Add to path string to loops."
		self.controlPoints = None
		self.loops = loops
		self.oldPoint = None
		self.outlinePaths = []
		self.path = []
		self.xmlElement = xmlElement
		self.yAxisPointingUpward = yAxisPointingUpward
		pathString = xmlElement.attributeDictionary['d'].replace(',', ' ')
		global globalProcessPathWordDictionary
		processPathWordDictionaryKeys = globalProcessPathWordDictionary.keys()
		for processPathWordDictionaryKey in processPathWordDictionaryKeys:
			pathString = pathString.replace( processPathWordDictionaryKey, ' %s ' % processPathWordDictionaryKey )
		self.words = getRightStripMinusSplit(pathString)
		for self.wordIndex in xrange( len( self.words ) ):
			word = self.words[ self.wordIndex ]
			if word in processPathWordDictionaryKeys:
				globalProcessPathWordDictionary[word](self)
		if len(self.path) > 0:
			self.outlinePaths.append(self.path)
		self.loops += getTransformedOutlineByPaths(self.outlinePaths, xmlElement, yAxisPointingUpward)

	def addPathArc( self, end ):
		"Add an arc to the path."
		begin = self.getOldPoint()
		self.controlPoints = None
		radius = self.getComplexByExtraIndex(1)
		xAxisRotation = math.radians(float(self.words[self.wordIndex + 3]))
		largeArcFlag = euclidean.getBooleanFromValue(self.words[ self.wordIndex + 4 ])
		sweepFlag = euclidean.getBooleanFromValue(self.words[ self.wordIndex + 5 ])
		self.path += getArcComplexes(begin, end, largeArcFlag, radius, sweepFlag, xAxisRotation)
		self.wordIndex += 8

	def addPathCubic( self, controlPoints, end ):
		"Add a cubic curve to the path."
		begin = self.getOldPoint()
		self.controlPoints = controlPoints
		self.path += getCubicPoints( begin, controlPoints, end )
		self.wordIndex += 7

	def addPathCubicReflected( self, controlPoint, end ):
		"Add a cubic curve to the path from a reflected control point."
		begin = self.getOldPoint()
		controlPointBegin = begin
		if self.controlPoints != None:
			if len(self.controlPoints) == 2:
				controlPointBegin = begin + begin - self.controlPoints[-1]
		self.controlPoints = [controlPointBegin, controlPoint]
		self.path += getCubicPoints(begin, self.controlPoints, end)
		self.wordIndex += 5

	def addPathLine(self, lineFunction, point):
		"Add a line to the path."
		self.controlPoints = None
		self.path.append(point)
		self.wordIndex += 3
		self.addPathLineByFunction(lineFunction)

	def addPathLineAxis(self, point):
		"Add an axis line to the path."
		self.controlPoints = None
		self.path.append(point)
		self.wordIndex += 2

	def addPathLineByFunction( self, lineFunction ):
		"Add a line to the path by line function."
		while 1:
			if self.getFloatByExtraIndex() == None:
				return
			self.path.append(lineFunction())
			self.wordIndex += 2

	def addPathMove( self, lineFunction, point ):
		"Add an axis line to the path."
		self.controlPoints = None
		if len(self.path) > 0:
			self.outlinePaths.append(self.path)
			self.oldPoint = self.path[-1]
		self.path = [point]
		self.wordIndex += 3
		self.addPathLineByFunction(lineFunction)

	def addPathQuadratic( self, controlPoint, end ):
		"Add a quadratic curve to the path."
		begin = self.getOldPoint()
		self.controlPoints = [controlPoint]
		self.path += getQuadraticPoints(begin, controlPoint, end)
		self.wordIndex += 5

	def addPathQuadraticReflected( self, end ):
		"Add a quadratic curve to the path from a reflected control point."
		begin = self.getOldPoint()
		controlPoint = begin
		if self.controlPoints != None:
			if len( self.controlPoints ) == 1:
				controlPoint = begin + begin - self.controlPoints[-1]
		self.controlPoints = [ controlPoint ]
		self.path += getQuadraticPoints(begin, controlPoint, end)
		self.wordIndex += 3

	def getComplexByExtraIndex( self, extraIndex=0 ):
		'Get complex from the extraIndex.'
		return euclidean.getComplexByWords(self.words, self.wordIndex + extraIndex)

	def getComplexRelative(self):
		"Get relative complex."
		return self.getComplexByExtraIndex() + self.getOldPoint()

	def getFloatByExtraIndex( self, extraIndex=0 ):
		'Get float from the extraIndex.'
		totalIndex = self.wordIndex + extraIndex
		if totalIndex >= len(self.words):
			return None
		word = self.words[totalIndex]
		if word[: 1].isalpha():
			return None
		return euclidean.getFloatFromValue(word)

	def getOldPoint(self):
		'Get the old point.'
		if len(self.path) > 0:
			return self.path[-1]
		return self.oldPoint

	def processPathWordA(self):
		'Process path word A.'
		self.addPathArc( self.getComplexByExtraIndex( 6 ) )

	def processPathWorda(self):
		'Process path word a.'
		self.addPathArc(self.getComplexByExtraIndex(6) + self.getOldPoint())

	def processPathWordC(self):
		'Process path word C.'
		end = self.getComplexByExtraIndex( 5 )
		self.addPathCubic( [ self.getComplexByExtraIndex( 1 ), self.getComplexByExtraIndex( 3 ) ], end )

	def processPathWordc(self):
		'Process path word C.'
		begin = self.getOldPoint()
		end = self.getComplexByExtraIndex( 5 )
		self.addPathCubic( [ self.getComplexByExtraIndex( 1 ) + begin, self.getComplexByExtraIndex( 3 ) + begin ], end + begin )

	def processPathWordH(self):
		"Process path word H."
		beginY = self.getOldPoint().imag
		self.addPathLineAxis(complex(float(self.words[self.wordIndex + 1]), beginY))
		while 1:
			floatByExtraIndex = self.getFloatByExtraIndex()
			if floatByExtraIndex == None:
				return
			self.path.append(complex(floatByExtraIndex, beginY))
			self.wordIndex += 1

	def processPathWordh(self):
		"Process path word h."
		begin = self.getOldPoint()
		self.addPathLineAxis(complex(float(self.words[self.wordIndex + 1]) + begin.real, begin.imag))
		while 1:
			floatByExtraIndex = self.getFloatByExtraIndex()
			if floatByExtraIndex == None:
				return
			self.path.append(complex(floatByExtraIndex + self.getOldPoint().real, begin.imag))
			self.wordIndex += 1

	def processPathWordL(self):
		"Process path word L."
		self.addPathLine(self.getComplexByExtraIndex, self.getComplexByExtraIndex( 1 ))

	def processPathWordl(self):
		"Process path word l."
		self.addPathLine(self.getComplexRelative, self.getComplexByExtraIndex(1) + self.getOldPoint())

	def processPathWordM(self):
		"Process path word M."
		self.addPathMove(self.getComplexByExtraIndex, self.getComplexByExtraIndex(1))

	def processPathWordm(self):
		"Process path word m."
		self.addPathMove(self.getComplexRelative, self.getComplexByExtraIndex(1) + self.getOldPoint())

	def processPathWordQ(self):
		'Process path word Q.'
		self.addPathQuadratic( self.getComplexByExtraIndex( 1 ), self.getComplexByExtraIndex( 3 ) )

	def processPathWordq(self):
		'Process path word q.'
		begin = self.getOldPoint()
		self.addPathQuadratic(self.getComplexByExtraIndex(1) + begin, self.getComplexByExtraIndex(3) + begin)

	def processPathWordS(self):
		'Process path word S.'
		self.addPathCubicReflected( self.getComplexByExtraIndex( 1 ), self.getComplexByExtraIndex( 3 ) )

	def processPathWords(self):
		'Process path word s.'
		begin = self.getOldPoint()
		self.addPathCubicReflected(self.getComplexByExtraIndex(1) + begin, self.getComplexByExtraIndex(3) + begin)

	def processPathWordT(self):
		'Process path word T.'
		self.addPathQuadraticReflected( self.getComplexByExtraIndex( 1 ) )

	def processPathWordt(self):
		'Process path word t.'
		self.addPathQuadraticReflected(self.getComplexByExtraIndex(1) + self.getOldPoint())

	def processPathWordV(self):
		"Process path word V."
		beginX = self.getOldPoint().real
		self.addPathLineAxis(complex(beginX, float(self.words[self.wordIndex + 1])))
		while 1:
			floatByExtraIndex = self.getFloatByExtraIndex()
			if floatByExtraIndex == None:
				return
			self.path.append(complex(beginX, floatByExtraIndex))
			self.wordIndex += 1

	def processPathWordv(self):
		"Process path word v."
		begin = self.getOldPoint()
		self.addPathLineAxis(complex(begin.real, float(self.words[self.wordIndex + 1]) + begin.imag))
		while 1:
			floatByExtraIndex = self.getFloatByExtraIndex()
			if floatByExtraIndex == None:
				return
			self.path.append(complex(begin.real, floatByExtraIndex + self.getOldPoint().imag))
			self.wordIndex += 1

	def processPathWordZ(self):
		"Process path word Z."
		self.controlPoints = None
		if len(self.path) < 1:
			return
		self.loops.append(getChainMatrixSVGIfNecessary(self.xmlElement, self.yAxisPointingUpward).getTransformedPath(self.path))
		self.oldPoint = self.path[0]
		self.path = []

	def processPathWordz(self):
		"Process path word z."
		self.processPathWordZ()


class SVGReader:
	"An svg carving."
	def __init__(self):
		"Add empty lists."
		self.bridgeRotation = None
		self.rotatedLoopLayers = []
		self.stopProcessing = False
		self.z = 0.0

	def flipDirectLayer(self, rotatedLoopLayer):
		"Flip the y coordinate of the layer and direct the loops."
		for loop in rotatedLoopLayer.loops:
			for pointIndex, point in enumerate(loop):
				loop[pointIndex] = complex(point.real, -point.imag)
		rotatedLoopLayer.loops = trianglemesh.getLoopsInOrderOfArea(trianglemesh.compareAreaDescending, rotatedLoopLayer.loops)
		for loopIndex, loop in enumerate(rotatedLoopLayer.loops):
			isInsideLoops = euclidean.getIsInFilledRegion(rotatedLoopLayer.loops[: loopIndex], euclidean.getLeftPoint(loop))
			intercircle.directLoop((not isInsideLoops), loop)

	def getRotatedLoopLayer(self):
		"Return the rotated loop layer."
		if self.z != None:
			rotatedLoopLayer = euclidean.RotatedLoopLayer( self.z )
			self.rotatedLoopLayers.append( rotatedLoopLayer )
			rotatedLoopLayer.rotation = self.bridgeRotation
			self.z = None
		return self.rotatedLoopLayers[-1]

	def parseSVG(self, fileName, svgText):
		"Parse SVG text and store the layers."
		self.fileName = fileName
		xmlParser = XMLSimpleReader(fileName, None, svgText)
		self.parseSVGByXMLElement(xmlParser.getRoot())

	def parseSVGByXMLElement(self, xmlElement):
		"Parse SVG by xmlElement."
		self.sliceDictionary = svg_writer.getSliceDictionary(xmlElement)
		self.yAxisPointingUpward = euclidean.getBooleanFromDictionaryDefault(False, self.sliceDictionary, 'yAxisPointingUpward')
		self.processXMLElement(xmlElement)
		if not self.yAxisPointingUpward:
			for rotatedLoopLayer in self.rotatedLoopLayers:
				self.flipDirectLayer(rotatedLoopLayer)

	def processXMLElement(self, xmlElement):
		"Process the xml element."
		if self.stopProcessing:
			return
		lowerClassName = xmlElement.className.lower()
		global globalProcessSVGElementDictionary
		if lowerClassName in globalProcessSVGElementDictionary:
			try:
				globalProcessSVGElementDictionary[ lowerClassName ](self, xmlElement)
			except:
				print('Warning, in processXMLElement in svg_reader, could not process:')
				print(xmlElement)
				traceback.print_exc(file=sys.stdout)
		for child in xmlElement.children:
			self.processXMLElement( child )


globalFontFileNames = None
globalFontReaderDictionary = {}
globalGetTricomplexDictionary = {}
globalGetTricomplexFunctions = [
	getTricomplexmatrix,
	getTricomplexrotate,
	getTricomplexscale,
	getTricomplexskewX,
	getTricomplexskewY,
	getTricomplextranslate ]
globalProcessPathWordFunctions = [
	PathReader.processPathWordA,
	PathReader.processPathWorda,
	PathReader.processPathWordC,
	PathReader.processPathWordc,
	PathReader.processPathWordH,
	PathReader.processPathWordh,
	PathReader.processPathWordL,
	PathReader.processPathWordl,
	PathReader.processPathWordM,
	PathReader.processPathWordm,
	PathReader.processPathWordQ,
	PathReader.processPathWordq,
	PathReader.processPathWordS,
	PathReader.processPathWords,
	PathReader.processPathWordT,
	PathReader.processPathWordt,
	PathReader.processPathWordV,
	PathReader.processPathWordv,
	PathReader.processPathWordZ,
	PathReader.processPathWordz ]
globalProcessPathWordDictionary = {}
globalProcessSVGElementDictionary = {}
globalProcessSVGElementFunctions = [
	processSVGElementcircle,
	processSVGElementellipse,
	processSVGElementg,
	processSVGElementline,
	processSVGElementpath,
	processSVGElementpolygon,
	processSVGElementpolyline,
	processSVGElementrect,
	processSVGElementtext ]
globalSideAngle = 0.5 * math.pi / float( globalNumberOfCornerPoints )


addFunctionsToDictionary( globalGetTricomplexDictionary, globalGetTricomplexFunctions, 'getTricomplex')
addFunctionsToDictionary( globalProcessPathWordDictionary, globalProcessPathWordFunctions, 'processPathWord')
addFunctionsToDictionary( globalProcessSVGElementDictionary, globalProcessSVGElementFunctions, 'processSVGElement')
