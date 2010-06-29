"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_tools import matrix4x4
from fabmetheus_utilities.geometry.geometry_tools import path
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.solids import group
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def compareExecutionOrderAscending( module, otherModule ):
	"Get comparison in order to sort modules in ascending execution order."
	if module.getExecutionOrder() < otherModule.getExecutionOrder():
		return - 1
	return int( module.getExecutionOrder() > otherModule.getExecutionOrder() )

def getBevelLoop( close, loop, sideLength, xmlElement ):
	"Get bevel loop."
	radius = getRadiusByPrefix( 'bevel', sideLength, xmlElement )
	if radius == 0.0:
		return loop
	bevelLoop = []
	for pointIndex in xrange( len( loop ) ):
		begin = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ]
		center = loop[ pointIndex ]
		end = loop[ ( pointIndex + 1 ) % len( loop ) ]
		bevelLoop += getBevelPath( begin, center, close, end, radius )
	return euclidean.getLoopWithoutCloseSequentialPoints( close, bevelLoop )

def getBevelPath( begin, center, close, end, radius ):
	"Get bevel path."
	beginComplex = begin.dropAxis()
	centerComplex = center.dropAxis()
	endComplex = end.dropAxis()
	beginComplexSegmentLength = abs( centerComplex - beginComplex )
	endComplexSegmentLength = abs( centerComplex - endComplex )
	minimumRadius = getMinimumRadius( beginComplexSegmentLength, endComplexSegmentLength, radius )
	if minimumRadius <= close:
		return [ center ]
	beginBevel = center + minimumRadius / beginComplexSegmentLength * ( begin - center )
	endBevel = center + minimumRadius / endComplexSegmentLength * ( end - center )
	if radius > 0.0:
		return [ beginBevel, endBevel ]
	midpointComplex = 0.5 * ( beginBevel.dropAxis() + endBevel.dropAxis() )
	spikeComplex = centerComplex + centerComplex - midpointComplex
	return [ beginBevel, Vector3( spikeComplex.real, spikeComplex.imag, center.z ), endBevel ]

def getFloatByPrefixSide( prefix, side, xmlElement ):
	"Get float by prefix and side."
	floatByDenominatorPrefix = evaluate.getEvaluatedFloatZero( prefix, xmlElement )
	return floatByDenominatorPrefix + evaluate.getEvaluatedFloatZero( prefix + 'overside', xmlElement ) * side

def getGeometryOutput( xmlElement ):
	"Get geometry output from paths."
	return getGeometryOutputByFunction( None, xmlElement )

def getGeometryOutputByEquation( sideLoop, xmlElement ):
	"Get geometry output by manipulation."
	evaluate.alterVerticesByEquation( sideLoop.loop, xmlElement )
	sideLoop.loop = euclidean.getLoopWithoutCloseSequentialPoints( sideLoop.close, sideLoop.loop )
	sideLoop.loop = getSegmentLoop( sideLoop.close, sideLoop.loop, xmlElement )
	sideLoop.loop = getBevelLoop( sideLoop.close, sideLoop.loop, sideLoop.sideLength, xmlElement )
	sideLoop.loop = getRoundLoop( sideLoop.close, sideLoop.loop, sideLoop.sideLength, xmlElement )
	return sideLoop.getManipulationPluginLoops( xmlElement )

def getGeometryOutputByFunction( manipulationFunction, xmlElement ):
	"Get geometry output from paths and manipulationFunction."
	geometryOutput = []
	paths = evaluate.getPathsByKeys( [ 'path', 'paths', 'target' ], xmlElement )
	for path in paths:
		sideLoop = SideLoop( path )
		geometryOutput += getGeometryOutputByLoop( manipulationFunction, sideLoop, xmlElement )
	return getUnpackedLoops( geometryOutput )

def getGeometryOutputByLoop( manipulationFunction, sideLoop, xmlElement ):
	"Get geometry output by side loop."
	sideLoop.centerRotate( xmlElement )
	if manipulationFunction == None:
		return getUnpackedLoops( getGeometryOutputByEquation( sideLoop, xmlElement ) )
	loops = manipulationFunction( sideLoop.close, sideLoop.loop, '', xmlElement )
	geometryOutput = []
	for loop in loops:
		sideLoop.loop = loop
		geometryOutput += getGeometryOutputByEquation( sideLoop, xmlElement )
	return getUnpackedLoops( geometryOutput )

def getMinimumRadius( beginComplexSegmentLength, endComplexSegmentLength, radius ):
	"Get minimum radius."
	return min( abs( radius ), 0.5 * min( beginComplexSegmentLength, endComplexSegmentLength ) )

def getRadialPath( begin, end, path, segmentCenter ):
	"Get radial path."
	beginComplex = begin.dropAxis()
	endComplex = end.dropAxis()
	segmentCenterComplex = segmentCenter.dropAxis()
	beginMinusCenterComplex = beginComplex - segmentCenterComplex
	endMinusCenterComplex = endComplex - segmentCenterComplex
	beginMinusCenterComplexRadius = abs( beginMinusCenterComplex )
	endMinusCenterComplexRadius = abs( endMinusCenterComplex )
	if beginMinusCenterComplexRadius == 0.0 or endMinusCenterComplexRadius == 0.0:
		return [ begin ]
	beginMinusCenterComplex /= beginMinusCenterComplexRadius
	endMinusCenterComplex /= endMinusCenterComplexRadius
	angleDifference = euclidean.getAngleDifferenceByComplex( endMinusCenterComplex, beginMinusCenterComplex )
	radialPath = []
	for point in path:
		weightEnd = point.x
		weightBegin = 1.0 - weightEnd
		weightedRadius = beginMinusCenterComplexRadius * weightBegin + endMinusCenterComplexRadius * weightEnd + point.y
		radialComplex = weightedRadius * euclidean.getWiddershinsUnitPolar( angleDifference * point.x ) * beginMinusCenterComplex
		polygonPoint = segmentCenter + Vector3( radialComplex.real, radialComplex.imag, point.z )
		radialPath.append( polygonPoint )
	return radialPath

def getRadiusByPrefix( prefix, sideLength, xmlElement ):
	"Get radius by prefix."
	radius = getFloatByPrefixSide( prefix, sideLength, xmlElement )
	radius += getFloatByPrefixSide( prefix + 'radius', sideLength, xmlElement )
	return radius + 0.5 * getFloatByPrefixSide( prefix + 'diameter', sideLength, xmlElement )

def getRoundLoop( close, loop, sideLength, xmlElement ):
	"Get round loop."
	radius = getRadiusByPrefix( 'round', sideLength, xmlElement )
	if radius == 0.0:
		return loop
	roundLoop = []
	sidesPerRadian = 0.5 / math.pi * evaluate.getSides( sideLength, xmlElement )
	for pointIndex in xrange( len( loop ) ):
		begin = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ]
		center = loop[ pointIndex ]
		end = loop[ ( pointIndex + 1 ) % len( loop ) ]
		roundLoop += getRoundPath( begin, center, close, end, radius, sidesPerRadian )
	return euclidean.getLoopWithoutCloseSequentialPoints( close, roundLoop )

def getRoundPath( begin, center, close, end, radius, sidesPerRadian ):
	"Get round path."
	beginComplex = begin.dropAxis()
	centerComplex = center.dropAxis()
	endComplex = end.dropAxis()
	beginComplexSegmentLength = abs( centerComplex - beginComplex )
	endComplexSegmentLength = abs( centerComplex - endComplex )
	minimumRadius = getMinimumRadius( beginComplexSegmentLength, endComplexSegmentLength, radius )
	if minimumRadius <= close:
		return [ center ]
	beginBevel = center + minimumRadius / beginComplexSegmentLength * ( begin - center )
	endBevel = center + minimumRadius / endComplexSegmentLength * ( end - center )
	beginBevelComplex = beginBevel.dropAxis()
	endBevelComplex = endBevel.dropAxis()
	midpointComplex = 0.5 * ( beginBevelComplex + endBevelComplex )
	if radius < 0.0:
		centerComplex = midpointComplex + midpointComplex - centerComplex
	midpointMinusCenterComplex = midpointComplex - centerComplex
	midpointCenterLength = abs( midpointMinusCenterComplex )
	midpointEndLength = abs( midpointComplex - endBevelComplex )
	midpointCircleCenterLength = midpointEndLength * midpointEndLength / midpointCenterLength
	circleRadius = math.sqrt( midpointCircleCenterLength * midpointCircleCenterLength + midpointEndLength * midpointEndLength )
	circleCenterComplex = midpointComplex + midpointMinusCenterComplex * midpointCircleCenterLength / midpointCenterLength
	circleCenter = Vector3( circleCenterComplex.real, circleCenterComplex.imag, center.z )
	endMinusCircleCenterComplex = endBevelComplex - circleCenterComplex
	beginMinusCircleCenter = beginBevel - circleCenter
	beginMinusCircleCenterComplex = beginMinusCircleCenter.dropAxis( 2 )
	angleDifference = euclidean.getAngleDifferenceByComplex( endMinusCircleCenterComplex, beginMinusCircleCenterComplex )
	steps = int( math.ceil( abs( angleDifference ) * sidesPerRadian ) )
	stepPlaneAngle = euclidean.getWiddershinsUnitPolar( angleDifference / float( steps ) )
	deltaZStep = ( end.z - begin.z ) / float( steps )
	roundPath = [ beginBevel ]
	for step in xrange( 1, steps ):
		beginMinusCircleCenterComplex = beginMinusCircleCenterComplex * stepPlaneAngle
		arcPointComplex = circleCenterComplex + beginMinusCircleCenterComplex
		arcPoint = Vector3( arcPointComplex.real, arcPointComplex.imag, begin.z + deltaZStep * step )
		roundPath.append( arcPoint )
	return roundPath + [ endBevel ]

def getSegmentLoop( close, loop, xmlElement ):
	"Get segment loop."
	path = evaluate.getPathByPrefix( getSegmentPathDefault(), 'segment', xmlElement )
	if path == getSegmentPathDefault():
		return loop
	path = getXNormalizedVector3Path( path )
	segmentCenter = evaluate.getVector3ByKey( 'segmentcenter', None, xmlElement )
	if euclidean.getIsWiddershinsByVector3( loop ):
		path = path[ : : - 1 ]
		for point in path:
			point.x = 1.0 - point.x
			if segmentCenter == None:
				point.y = - point.y
	segmentLoop = []
	for pointIndex in xrange( len( loop ) ):
		segmentLoop += getSegmentPath( loop, path, pointIndex, segmentCenter )
	return euclidean.getLoopWithoutCloseSequentialPoints( close, segmentLoop )

def getSegmentPath( loop, path, pointIndex, segmentCenter ):
	"Get segment path."
	centerBegin = loop[ pointIndex ]
	centerEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
	centerEndMinusBegin = centerEnd - centerBegin
	if abs( centerEndMinusBegin ) <= 0.0:
		return [ centerBegin ]
	if segmentCenter != None:
		return getRadialPath( centerBegin, centerEnd, path, segmentCenter )
	begin = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ]
	end = loop[ ( pointIndex + 2 ) % len( loop ) ]
	return getWedgePath( begin, centerBegin, centerEnd, centerEndMinusBegin, end, path )

def getUnpackedLoops( loops ):
	"Get unpacked loops."
	if len( loops ) == 1:
		firstLoop = loops[ 0 ]
		if firstLoop.__class__ == list:
			return firstLoop
	return loops

def getWedgePath( begin, centerBegin, centerEnd, centerEndMinusBegin, end, path ):
	"Get segment path."
	beginComplex = begin.dropAxis()
	centerBeginComplex = centerBegin.dropAxis()
	centerEndComplex = centerEnd.dropAxis()
	endComplex = end.dropAxis()
	wedgePath = []
	centerBeginMinusBeginComplex = euclidean.getNormalized( centerBeginComplex - beginComplex )
	centerEndMinusCenterBeginComplex = euclidean.getNormalized( centerEndComplex - centerBeginComplex )
	endMinusCenterEndComplex = euclidean.getNormalized( endComplex - centerEndComplex )
	widdershinsBegin = getWiddershinsAverageByVector3( centerBeginMinusBeginComplex, centerEndMinusCenterBeginComplex )
	widdershinsEnd = getWiddershinsAverageByVector3( centerEndMinusCenterBeginComplex, endMinusCenterEndComplex )
	for point in path:
		weightEnd = point.x
		weightBegin = 1.0 - weightEnd
		polygonPoint = centerBegin + centerEndMinusBegin * point.x
		weightedWiddershins = widdershinsBegin * weightBegin + widdershinsEnd * weightEnd
		polygonPoint += weightedWiddershins * point.y
		polygonPoint.z += point.z
		wedgePath.append( polygonPoint )
	return wedgePath

def getSegmentPathDefault():
	"Get segment path default."
	return [ Vector3(), Vector3( 0.0, 1.0 ) ]

def getXNormalizedVector3Path( path ):
	"Get path where the x ranges from 0 to 1."
	if len( path ) < 1:
		return path
	minimumX = path[ 0 ].x
	for point in path[ 1 : ]:
		minimumX = min( minimumX, point.x )
	for point in path:
		point.x -= minimumX
	maximumX = path[ 0 ].x
	for point in path[ 1 : ]:
		maximumX = max( maximumX, point.x )
	for point in path:
		point.x /= maximumX
	return path

def getWiddershinsAverageByVector3( centerMinusBeginComplex, endMinusCenterComplex ):
	"Get the normalized average of the widdershins vectors."
	centerMinusBeginWiddershins = Vector3( - centerMinusBeginComplex.imag, centerMinusBeginComplex.real )
	endMinusCenterWiddershins = Vector3( - endMinusCenterComplex.imag, endMinusCenterComplex.real )
	return ( centerMinusBeginWiddershins + endMinusCenterWiddershins ).getNormalized()

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	processXMLElementByGeometry( getGeometryOutput( xmlElement ), xmlElement, xmlProcessor )

def processXMLElementByFunction( manipulationFunction, xmlElement, xmlProcessor ):
	"Process the xml element by manipulationFunction."
	geometryOutput = getGeometryOutputByFunction( manipulationFunction, xmlElement )
	processXMLElementByGeometry( geometryOutput, xmlElement, xmlProcessor )

def processXMLElementByGeometry( geometryOutput, xmlElement, xmlProcessor ):
	"Process the xml element by geometryOutput."
	firstElement = None
	if len( geometryOutput ) > 0:
		firstElement = geometryOutput[ 0 ]
	if firstElement.__class__ == list:
		if len( firstElement ) > 1:
			group.convertXMLElementRenameByPaths( geometryOutput, xmlElement, xmlProcessor )
		else:
			path.convertXMLElementRename( firstElement, xmlElement, xmlProcessor )
	else:
		path.convertXMLElementRename( geometryOutput, xmlElement, xmlProcessor )
	xmlProcessor.processXMLElement( xmlElement )

def transformIfFromEvaluatorCreation( path, xmlElement ):
	"Transform the path if the xmlElement came from a EvaluatorCreation."
	if not evaluate.getEvaluatedBooleanDefault( False, '_fromEvaluatorCreation', xmlElement ):
		return
	xmlElementMatrix = matrix4x4.Matrix4X4().getFromXMLElement( xmlElement )
	if xmlElementMatrix.getIsDefault():
		return
	for point in path:
		point.setToVector3( matrix4x4.getVector3TransformedByMatrix( xmlElementMatrix.matrixTetragrid, point ) )

def transformIfFromEvaluatorCreationByPaths( paths, xmlElement ):
	"Transform the paths if the xmlElement came from a EvaluatorCreation."
	for path in paths:
		transformIfFromEvaluatorCreation( path, xmlElement )


class SideLoop:
	"Class to handle loop, side angle and side length."
	def __init__( self, loop, sideAngle = None, sideLength = None ):
		"Initialize."
		if sideAngle == None:
			sideAngle = 2.0 * math.pi / float( len( loop ) )
		if sideLength == None:
			sideLength = euclidean.getPolygonLength( loop ) / float( len( loop ) )
		self.loop = loop
		self.sideAngle = abs( sideAngle )
		self.sideLength = sideLength
		self.close = 0.001 * sideLength

	def centerRotate( self, xmlElement ):
		"Add a wedge center and rotate."
		wedgeCenter = evaluate.getVector3ByKey( 'wedgecenter', None, xmlElement )
		if wedgeCenter != None:
			self.loop.append( wedgeCenter )
		rotation = math.radians( evaluate.getEvaluatedFloatZero( 'rotation', xmlElement ) )
		rotation += evaluate.getEvaluatedFloatZero( 'rotationoverside', xmlElement ) * self.sideAngle
		if rotation != 0.0:
			planeRotation = euclidean.getWiddershinsUnitPolar( rotation )
			for vertex in self.loop:
				rotatedComplex = vertex.dropAxis() * planeRotation
				vertex.x = rotatedComplex.real
				vertex.y = rotatedComplex.imag
		if 'clockwise' in xmlElement.attributeDictionary:
			isClockwise = euclidean.getBooleanFromValue( evaluate.getEvaluatedValueObliviously( 'clockwise', xmlElement ) )
			if isClockwise == euclidean.getIsWiddershinsByVector3( self.loop ):
				self.loop.reverse()

	def getManipulationPluginLoops( self, xmlElement ):
		"Get loop manipulated by the plugins in the manipulation paths folder."
		xmlProcessor = xmlElement.getXMLProcessor()
		matchingPlugins = evaluate.getMatchingPlugins( xmlProcessor.manipulationPathDictionary, xmlElement )
		matchingPlugins += evaluate.getMatchingPlugins( xmlProcessor.manipulationShapeDictionary, xmlElement )
		matchingPlugins.sort( compareExecutionOrderAscending )
		loops = [ self.loop ]
		for matchingPlugin in matchingPlugins:
			matchingLoops = []
			prefix = matchingPlugin.__name__ + '.'
			for loop in loops:
				matchingLoops += matchingPlugin.getManipulatedPaths( self.close, loop, prefix, xmlElement )
			loops = matchingLoops
		transformIfFromEvaluatorCreationByPaths( loops, xmlElement )
		return loops
