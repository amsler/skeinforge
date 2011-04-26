"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.manipulation_evaluator import matrix
from fabmetheus_utilities.geometry.geometry_tools import path
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getAverageRadius(radiusComplex):
	"Get average radius from radiusComplex."
	if radiusComplex.real == radiusComplex.imag:
		return radiusComplex.real
	return math.sqrt(radiusComplex.real * radiusComplex.imag)

def getComplexByDictionary(dictionary, valueComplex):
	"Get complex by dictionary."
	if 'x' in dictionary:
		valueComplex = complex(euclidean.getFloatFromValue(dictionary['x']),valueComplex.imag)
	if 'y' in dictionary:
		valueComplex = complex(valueComplex.real, euclidean.getFloatFromValue(dictionary['y']))
	return valueComplex

def getComplexByDictionaryListValue(value, valueComplex):
	"Get complex by dictionary, list or value."
	if value.__class__ == complex:
		return value
	if value.__class__ == dict:
		return getComplexByDictionary(value, valueComplex)
	if value.__class__ == list:
		return getComplexByFloatList(value, valueComplex)
	floatFromValue = euclidean.getFloatFromValue(value)
	if floatFromValue ==  None:
		return valueComplex
	return complex( floatFromValue, floatFromValue )

def getComplexByFloatList( floatList, valueComplex ):
	"Get complex by float list."
	if len(floatList) > 0:
		valueComplex = complex(euclidean.getFloatFromValue(floatList[0]), valueComplex.imag)
	if len(floatList) > 1:
		valueComplex = complex(valueComplex.real, euclidean.getFloatFromValue(floatList[1]))
	return valueComplex

def getComplexByMultiplierPrefix( multiplier, prefix, valueComplex, xmlElement ):
	"Get complex from multiplier, prefix and xml element."
	if multiplier == 0.0:
		return valueComplex
	oldMultipliedValueComplex = valueComplex * multiplier
	complexByPrefix = getComplexByPrefix( prefix, oldMultipliedValueComplex, xmlElement )
	if complexByPrefix == oldMultipliedValueComplex:
		return valueComplex
	return complexByPrefix / multiplier

def getComplexByMultiplierPrefixes( multiplier, prefixes, valueComplex, xmlElement ):
	"Get complex from multiplier, prefixes and xml element."
	for prefix in prefixes:
		valueComplex = getComplexByMultiplierPrefix( multiplier, prefix, valueComplex, xmlElement )
	return valueComplex

def getComplexByPrefix( prefix, valueComplex, xmlElement ):
	"Get complex from prefix and xml element."
	value = evaluate.getEvaluatedValue(prefix, xmlElement)
	if value != None:
		valueComplex = getComplexByDictionaryListValue(value, valueComplex)
	x = evaluate.getEvaluatedFloat(prefix + '.x', xmlElement)
	if x != None:
		valueComplex = complex( x, getComplexIfNone( valueComplex ).imag )
	y = evaluate.getEvaluatedFloat(prefix + '.y', xmlElement)
	if y != None:
		valueComplex = complex( getComplexIfNone( valueComplex ).real, y )
	return valueComplex

def getComplexByPrefixBeginEnd(prefixBegin, prefixEnd, valueComplex, xmlElement):
	"Get complex from prefixBegin, prefixEnd and xml element."
	valueComplex = getComplexByPrefix(prefixBegin, valueComplex, xmlElement)
	if prefixEnd in xmlElement.attributeDictionary:
		return 0.5 * getComplexByPrefix(valueComplex + valueComplex, prefixEnd, xmlElement)
	else:
		return valueComplex

def getComplexByPrefixes( prefixes, valueComplex, xmlElement ):
	"Get complex from prefixes and xml element."
	for prefix in prefixes:
		valueComplex = getComplexByPrefix( prefix, valueComplex, xmlElement )
	return valueComplex

def getComplexIfNone( valueComplex ):
	"Get new complex if the original complex is none."
	if valueComplex == None:
		return complex()
	return valueComplex

def getRadiusComplex(radius, xmlElement):
	"Get radius complex for xmlElement."
	radius = getComplexByPrefixes(['demisize', 'radius'], radius, xmlElement)
	return getComplexByMultiplierPrefixes(2.0, ['diameter', 'size'], radius, xmlElement)

def getFloatByPrefixBeginEnd( prefixBegin, prefixEnd, valueFloat, xmlElement ):
	"Get float from prefixBegin, prefixEnd and xml element."
	valueFloat = evaluate.getEvaluatedFloatDefault( valueFloat, prefixBegin, xmlElement )
	if prefixEnd in xmlElement.attributeDictionary:
		return 0.5 * evaluate.getEvaluatedFloatDefault( valueFloat + valueFloat, prefixEnd, xmlElement )
	else:
		return valueFloat

def getFloatByPrefixSide( prefix, side, xmlElement ):
	"Get float by prefix and side."
	floatByDenominatorPrefix = evaluate.getEvaluatedFloatZero(prefix, xmlElement)
	return floatByDenominatorPrefix + evaluate.getEvaluatedFloatZero( prefix + 'OverSide', xmlElement ) * side

def getGeometryOutput(xmlElement):
	"Get geometry output from paths."
	geometryOutput = []
	paths = evaluate.getPathsByKeys( ['path', 'paths', 'target'], xmlElement )
	for path in paths:
		sideLoop = SideLoop(path)
		geometryOutput += getGeometryOutputByLoop( sideLoop, xmlElement )
	return getUnpackedLoops(geometryOutput)

def getGeometryOutputByArguments(arguments, xmlElement):
	"Get vector3 vertexes from attribute dictionary by arguments."
	return getGeometryOutput(xmlElement)

def getGeometryOutputByFunction( manipulationFunction, xmlElement ):
	"Get geometry output by manipulationFunction."
	geometryOutput = []
	paths = evaluate.getPathsByKey('target', xmlElement )
	for path in paths:
		geometryOutput += getGeometryOutputByLoopFunction( manipulationFunction, SideLoop(path), xmlElement )
	return getUnpackedLoops(geometryOutput)

def getGeometryOutputByLoop( sideLoop, xmlElement ):
	"Get geometry output by side loop."
	sideLoop.rotate(xmlElement)
	return getUnpackedLoops( getGeometryOutputByManipulation( sideLoop, xmlElement ) )

def getGeometryOutputByLoopFunction( manipulationFunction, sideLoop, xmlElement ):
	"Get geometry output by side loop."
	sideLoop.rotate(xmlElement)
	sideLoop.loop = euclidean.getLoopWithoutCloseSequentialPoints( sideLoop.close, sideLoop.loop )
	return getUnpackedLoops( manipulationFunction( sideLoop.close, sideLoop.loop, '', sideLoop.sideLength, xmlElement ) )

def getGeometryOutputByManipulation( sideLoop, xmlElement ):
	"Get geometry output by manipulation."
	sideLoop.loop = euclidean.getLoopWithoutCloseSequentialPoints( sideLoop.close, sideLoop.loop )
	return sideLoop.getManipulationPluginLoops(xmlElement)

def getMinimumRadius( beginComplexSegmentLength, endComplexSegmentLength, radius ):
	"Get minimum radius."
	return min( abs(radius), 0.5 * min( beginComplexSegmentLength, endComplexSegmentLength ) )

def getNumberOfBezierPoints(begin, end, xmlElement):
	"Get the numberOfBezierPoints."
	numberOfBezierPoints = int(math.ceil(0.5 * evaluate.getSidesMinimumThreeBasedOnPrecision(abs(end - begin), xmlElement)))
	return evaluate.getEvaluatedIntDefault(numberOfBezierPoints, 'sides', xmlElement)

def getRadiusByPrefix(prefix, sideLength, xmlElement):
	"Get radius by prefix."
	radius = getFloatByPrefixSide(prefix + 'radius', sideLength, xmlElement)
	radius += 0.5 * getFloatByPrefixSide(prefix + 'diameter', sideLength, xmlElement)
	return radius + 0.5 * getFloatByPrefixSide(prefix + 'size', sideLength, xmlElement)

def getStrokeRadiusByPrefix(prefix, xmlElement):
	"Get strokeRadius by prefix."
	strokeRadius = getFloatByPrefixBeginEnd(prefix + 'strokeRadius', prefix + 'strokeWidth', 1.0, xmlElement )
	return getFloatByPrefixBeginEnd(prefix + 'radius', prefix + 'diameter', strokeRadius, xmlElement )

def getUnpackedLoops( loops ):
	"Get unpacked loops."
	if len( loops ) == 1:
		firstLoop = loops[0]
		if firstLoop.__class__ == list:
			return firstLoop
	return loops

def getWrappedInteger( integer, modulo ):
	"Get wrapped integer."
	if integer >= modulo:
		return modulo
	if integer >= 0:
		return integer
	return integer % modulo

def processXMLElement(xmlElement):
	"Process the xml element."
	processXMLElementByGeometry(getGeometryOutput(xmlElement), xmlElement)

def processXMLElementByFunction(manipulationFunction, xmlElement):
	"Process the xml element by manipulationFunction."
	geometryOutput = getGeometryOutputByFunction(manipulationFunction, xmlElement)
	processXMLElementByGeometry(geometryOutput, xmlElement)

def processXMLElementByGeometry(geometryOutput, xmlElement):
	"Process the xml element by geometryOutput."
	if geometryOutput == None:
		return
	geometryOutput = evaluate.getVector3ListsRecursively(geometryOutput)
	if 'target' in xmlElement.attributeDictionary and not evaluate.getEvaluatedBooleanDefault(False, 'copy', xmlElement):
		target = evaluate.getEvaluatedLinkValue(str(xmlElement.attributeDictionary['target']).strip(), xmlElement)
		if target.__class__.__name__ == 'XMLElement':
			target.removeChildrenFromIDNameParent()
			xmlElement = target
			if xmlElement.object != None:
				if xmlElement.parent.object != None:
					if xmlElement.object in xmlElement.parent.object.archivableObjects:
						xmlElement.parent.object.archivableObjects.remove(xmlElement.object)
	firstElement = None
	if len(geometryOutput) > 0:
		firstElement = geometryOutput[0]
	if firstElement.__class__ == list:
		if len(firstElement) > 1:
			path.convertXMLElementRenameByPaths(geometryOutput, xmlElement)
		else:
			path.convertXMLElementRename(firstElement, xmlElement)
	else:
		path.convertXMLElementRename(geometryOutput, xmlElement)
	path.processXMLElement(xmlElement)

def setClosedAttribute(revolutions, xmlElement):
	"Set the closed attribute of the xmlElement."
	xmlElement.attributeDictionary['closed'] = str(evaluate.getEvaluatedBooleanDefault(revolutions <= 1, 'closed', xmlElement)).lower()


class SideLoop:
	"Class to handle loop, side angle and side length."
	def __init__( self, loop, sideAngle = None, sideLength = None ):
		"Initialize."
		if sideAngle == None:
			if len(loop) > 0:
				sideAngle = 2.0 * math.pi / float(len(loop))
			else:
				sideAngle = 1.0
				print('Warning, loop has no sides in SideLoop in lineation.')
		if sideLength == None:
			if len(loop) > 0:
				sideLength = euclidean.getLoopLength(loop) / float(len(loop))
			else:
				sideLength = 1.0
				print('Warning, loop has no length in SideLoop in lineation.')
		self.loop = loop
		self.sideAngle = abs( sideAngle )
		self.sideLength = sideLength
		self.close = 0.001 * sideLength

	def rotate(self, xmlElement):
		"Rotate."
		rotation = math.radians( evaluate.getEvaluatedFloatZero('rotation', xmlElement ) )
		rotation += evaluate.getEvaluatedFloatZero('rotationOverSide', xmlElement ) * self.sideAngle
		if rotation != 0.0:
			planeRotation = euclidean.getWiddershinsUnitPolar( rotation )
			for vertex in self.loop:
				rotatedComplex = vertex.dropAxis() * planeRotation
				vertex.x = rotatedComplex.real
				vertex.y = rotatedComplex.imag
		if 'clockwise' in xmlElement.attributeDictionary:
			isClockwise = euclidean.getBooleanFromValue( evaluate.getEvaluatedValueObliviously('clockwise', xmlElement ) )
			if isClockwise == euclidean.getIsWiddershinsByVector3( self.loop ):
				self.loop.reverse()

	def getManipulationPluginLoops(self, xmlElement):
		"Get loop manipulated by the plugins in the manipulation paths folder."
		xmlProcessor = xmlElement.getXMLProcessor()
		matchingPlugins = evaluate.getFromCreationEvaluatorPlugins(xmlProcessor.manipulationEvaluatorDictionary, xmlElement)
		matchingPlugins += evaluate.getMatchingPlugins(xmlProcessor.manipulationPathDictionary, xmlElement)
		matchingPlugins += evaluate.getMatchingPlugins(xmlProcessor.manipulationShapeDictionary, xmlElement)
		matchingPlugins.sort(evaluate.compareExecutionOrderAscending)
		loops = [self.loop]
		for matchingPlugin in matchingPlugins:
			matchingLoops = []
			prefix = matchingPlugin.__name__ + '.'
			for loop in loops:
				matchingLoops += matchingPlugin.getManipulatedPaths(self.close, loop, prefix, self.sideLength, xmlElement)
			loops = matchingLoops
		return loops


class Spiral:
	'Class to add a spiral.'
	def __init__(self, stepRatio, xmlElement):
		"Initialize."
		self.spiral = evaluate.getVector3ByPrefix('spiral', None, xmlElement)
		if self.spiral == None:
			return
		self.spiralIncrement = self.spiral * stepRatio
		self.spiralTotal = Vector3()

	def __repr__(self):
		"Get the string representation of this StartEnd."
		return self.spiral

	def getSpiralPoint(self, unitPolar, vector3):
		"Add spiral to the vector."
		if self.spiral == None:
			return vector3
		vector3 += Vector3(unitPolar.real * self.spiralTotal.x, unitPolar.imag * self.spiralTotal.y, self.spiralTotal.z)
		self.spiralTotal += self.spiralIncrement
		return vector3


class StartEnd:
	'Class to get a start through end range.'
	def __init__(self, modulo, prefix, xmlElement):
		"Initialize."
		self.start = evaluate.getEvaluatedIntZero(prefix + 'start', xmlElement)
		self.start = getWrappedInteger(self.start, modulo)
		self.extent = evaluate.getEvaluatedIntDefault(modulo - self.start, prefix + 'extent', xmlElement)
		self.end = evaluate.getEvaluatedIntDefault(self.start + self.extent, prefix + 'end', xmlElement)
		self.end = getWrappedInteger(self.end, modulo)
		self.revolutions = evaluate.getEvaluatedIntOne(prefix + 'revolutions', xmlElement)
		if self.revolutions > 1:
			self.end += modulo * (self.revolutions - 1)

	def __repr__(self):
		"Get the string representation of this StartEnd."
		return '%s, %s, %s' % (self.start, self.end, self.revolutions)
