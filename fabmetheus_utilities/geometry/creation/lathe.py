"""
Boolean geometry extrusion.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import lineation
from fabmetheus_utilities.geometry.creation import solid
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = 'GPL 3.0'

def addLoopByComplex(derivation, endMultiplier, loopLists, path, pointComplex, vertexes):
	"Add an indexed loop to the vertexes."
	loops = loopLists[-1]
	loop = []
	loops.append(loop)
	for point in path:
		pointMinusBegin = point - derivation.axisStart
		dotVector3 = derivation.axisProjectiveSpace.getDotVector3(pointMinusBegin)
		dotVector3Complex = dotVector3.dropAxis()
		dotPointComplex = pointComplex * dotVector3Complex
		dotPoint = Vector3(dotPointComplex.real, dotPointComplex.imag, dotVector3.z)
		projectedVector3 = derivation.axisProjectiveSpace.getVector3ByPoint(dotPoint) + derivation.axisStart
		loop.append(projectedVector3)

def addNegatives(derivation, negatives, paths):
	"Add pillars output to negatives."
	portionDirections = getSpacedPortionDirections(derivation.interpolationDictionary)
	for path in paths:
		endMultiplier = 1.000001
		geometryOutput = trianglemesh.getPillarsOutput(getLoopListsByPath(endMultiplier, derivation, path, portionDirections))
		negatives.append(geometryOutput)

def addNegativesPositives(derivation, negatives, paths, positives):
	"Add pillars output to negatives and positives."
	for path in paths:
		endMultiplier = None
		normal = euclidean.getNormalByPath(path)
		if normal.dot(derivation.normal) < 0.0:
			endMultiplier = 1.000001
		loopListsByPath = getLoopListsByPath(derivation, endMultiplier, path)
		geometryOutput = trianglemesh.getPillarsOutput(loopListsByPath)
		if endMultiplier == None:
			positives.append(geometryOutput)
		else:
			negatives.append(geometryOutput)

def addOffsetAddToLists( loop, offset, vector3Index, vertexes ):
	"Add an indexed loop to the vertexes."
	vector3Index += offset
	loop.append( vector3Index )
	vertexes.append( vector3Index )

def getGeometryOutput(derivation, xmlElement):
	"Get triangle mesh from attribute dictionary."
	if derivation == None:
		derivation = LatheDerivation()
		derivation.setToXMLElement(xmlElement)
	if len(euclidean.getConcatenatedList(derivation.target)) == 0:
		print('Warning, in lathe there are no paths.')
		print(xmlElement.attributeDictionary)
		return None
	negatives = []
	positives = []
	print(  derivation)
	addNegativesPositives(derivation, negatives, derivation.target, positives)
	return getGeometryOutputByNegativesPositives(derivation, negatives, positives, xmlElement)

def getGeometryOutputByArguments(arguments, xmlElement):
	"Get triangle mesh from attribute dictionary by arguments."
	return getGeometryOutput(None, xmlElement)

def getGeometryOutputByConnection(connectionEnd, connectionStart, geometryOutput, xmlElement):
	"Get solid output by connection."
	firstValue = geometryOutput.values()[0]
	firstValue['connectionStart'] = connectionStart
	firstValue['connectionEnd'] = connectionEnd
	return solid.getGeometryOutputByManipulation(geometryOutput, xmlElement)

def getGeometryOutputByNegativesPositives(derivation, negatives, positives, xmlElement):
	"Get triangle mesh from derivation, negatives, positives and xmlElement."
	positiveOutput = trianglemesh.getUnifiedOutput(positives)
	if len(negatives) < 1:
		return solid.getGeometryOutputByManipulation(positiveOutput, xmlElement)
	return solid.getGeometryOutputByManipulation({'difference' : {'shapes' : [positiveOutput] + negatives}}, xmlElement)##
	interpolationOffset = derivation.interpolationDictionary['offset']
	if len(negatives) < 1:
		return getGeometryOutputByOffset(positiveOutput, interpolationOffset, xmlElement)
	return getGeometryOutputByOffset({'difference' : {'shapes' : [positiveOutput] + negatives}}, interpolationOffset, xmlElement)

def getGeometryOutputByOffset( geometryOutput, interpolationOffset, xmlElement ):
	"Get solid output by interpolationOffset."
	geometryOutputValues = geometryOutput.values()
	if len(geometryOutputValues) < 1:
		return geometryOutput
	connectionStart = interpolationOffset.getVector3ByPortion(PortionDirection(0.0))
	connectionEnd = interpolationOffset.getVector3ByPortion(PortionDirection(1.0))
	return getGeometryOutputByConnection(connectionEnd, connectionStart, geometryOutput, xmlElement)

def getLoopListsByPath(derivation, endMultiplier, path):
	"Get loop lists from path."
	vertexes = []
	loopLists = [[]]
	if len(derivation.loop) < 2:
		return loopLists
	for pointIndex, pointComplex in enumerate(derivation.loop):
		if endMultiplier != None and derivation.end != derivation.start:
			if pointIndex == 0:
				nextPoint = derivation.loop[1]
				pointComplex = endMultiplier * (pointComplex - nextPoint) + nextPoint
			elif pointIndex == len(derivation.loop) - 1:
				previousPoint = derivation.loop[pointIndex - 1]
				pointComplex = endMultiplier * (pointComplex - previousPoint) + previousPoint
		addLoopByComplex(derivation, endMultiplier, loopLists, path, pointComplex, vertexes)
	if derivation.end == derivation.start:
		loopLists[-1].append([])
	return loopLists

def processXMLElement(xmlElement):
	"Process the xml element."
	solid.processXMLElementByGeometry(getGeometryOutput(None, xmlElement), xmlElement)


class LatheDerivation:
	"Class to hold lathe variables."
	def __init__(self):
		'Set defaults.'
		self.axisEnd = None
		self.axisStart = None
		self.end = 0.0
		self.loop = []
		self.sides = None
		self.start = 0.0

	def __repr__(self):
		"Get the string representation of this LatheDerivation."
		return str(self.__dict__)

	def derive(self, xmlElement):
		"Derive using the xmlElement."
		if len(self.target) < 1:
			print('Warning, no target in derive in lathe for:')
			print(xmlElement)
			return
		firstPath = self.target[0]
		if len(firstPath) < 3:
			print('Warning, firstPath length is less than three in derive in lathe for:')
			print(xmlElement)
			self.target = []
			return
		if self.axisStart == None:
			if self.axisEnd == None:
				self.axisStart = firstPath[0]
				self.axisEnd = firstPath[-1]
			else:
				self.axisStart = Vector3()
		self.axis = self.axisEnd - self.axisStart
		axisLength = abs(self.axis)
		if axisLength <= 0.0:
			print('Warning, axisLength is zero in derive in lathe for:')
			print(xmlElement)
			self.target = []
			return
		self.axis /= axisLength
		firstVector3 = firstPath[1] - self.axisStart
		firstVector3Length = abs(firstVector3)
		if firstVector3Length <= 0.0:
			print('Warning, firstVector3Length is zero in derive in lathe for:')
			print(xmlElement)
			self.target = []
			return
		firstVector3 /= firstVector3Length
		self.axisProjectiveSpace = euclidean.ProjectiveSpace().getByBasisZFirst(self.axis, firstVector3)
		if self.sides == None:
			distanceToLine = euclidean.getDistanceToLineByPaths(self.axisStart, self.axisEnd, self.target)
			self.sides = evaluate.getSidesMinimumThreeBasedOnPrecisionSides(distanceToLine, xmlElement)
		if len(self.loop) < 1:
			self.loop = euclidean.getComplexPolygonByStartEnd(math.radians(self.end), 1.0, self.sides, math.radians(self.start))
		self.normal = euclidean.getNormalByPath(firstPath)

	def setToXMLElement(self, xmlElement):
		"Set to the xmlElement."
		self.setToXMLElementOnly(xmlElement)
		self.derive(xmlElement)

	def setToXMLElementOnly(self, xmlElement):
		"Set to the xmlElement."
		self.axisEnd = evaluate.getVector3ByPrefix(self.axisEnd, 'axisEnd', xmlElement)
		self.axisStart = evaluate.getVector3ByPrefix(self.axisStart, 'axisStart', xmlElement)
		self.end = evaluate.getEvaluatedFloatDefault(self.end, 'end', xmlElement)
		self.loop = evaluate.getTransformedPathByKey('loop', xmlElement)
		self.sides = evaluate.getEvaluatedIntDefault(self.sides, 'sides', xmlElement)
		self.start = evaluate.getEvaluatedFloatDefault(self.start, 'start', xmlElement)
		self.target = evaluate.getTransformedPathsByKey('target', xmlElement)
