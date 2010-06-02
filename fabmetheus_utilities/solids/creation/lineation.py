"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools import path
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.solids import group
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


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
	floatByDenominatorPrefix = geomancer.getEvaluatedFloatZero( prefix, xmlElement )
	return floatByDenominatorPrefix + geomancer.getEvaluatedFloatZero( prefix + 'overside', xmlElement ) * side

def getGeometryOutput( xmlElement ):
	"Get geometry output from paths."
	return getGeometryOutputByFunction( None, xmlElement )

def getGeometryOutputByFunction( manipulationFunction, xmlElement ):
	"Get geometry output from paths and manipulationFunction."
	geometryOutput = []
	paths = geomancer.getPathsByKeys( [ 'path', 'paths', 'target' ], xmlElement )
	for path in paths:
		geometryOutput.append( getGeometryOutputByLoop( path, manipulationFunction, None, None, xmlElement ) )
	return geometryOutput

def getGeometryOutputByLoop( loop, manipulationFunction, sideAngle, sideLength, xmlElement ):
	"Get geometry output by loop."
	if sideAngle == None:
		sideAngle = 2.0 * math.pi / float( len( loop ) )
	if sideLength == None:
		sideLength = euclidean.getPolygonLength( loop ) / float( len( loop ) )
	wedgeCenter = geomancer.getVector3ByKey( 'wedgecenter', None, xmlElement )
	if wedgeCenter != None:
		loop.append( wedgeCenter )
	rotation = math.radians( geomancer.getEvaluatedFloatZero( 'rotation', xmlElement ) )
	rotation += geomancer.getEvaluatedFloatZero( 'rotationoverside', xmlElement ) * abs( sideAngle )
	if rotation != 0.0:
		planeRotation = euclidean.getWiddershinsUnitPolar( rotation )
		for vertex in loop:
			rotatedComplex = vertex.dropAxis() * planeRotation
			vertex.x = rotatedComplex.real
			vertex.y = rotatedComplex.imag
	if 'clockwise' in xmlElement.attributeDictionary:
		isClockwise = euclidean.getBooleanFromValue( geomancer.getEvaluatedValueObliviously( 'clockwise', xmlElement ) )
		if isClockwise == euclidean.getIsWiddershinsByVector3( loop ):
			loop.reverse()
	close = 0.001 * sideLength
	if manipulationFunction != None:
		loop = manipulationFunction( close, loop, xmlElement )
	geomancer.alterVerticesByEquation( loop, xmlElement )
	loop = euclidean.getLoopWithoutCloseSequentialPoints( close, loop )
	loop = getSegmentLoop( close, loop, xmlElement )
	loop = getBevelLoop( close, loop, sideLength, xmlElement )
	loop = getRoundLoop( close, loop, sideLength, xmlElement )
	loop = getManipulatorPathPluginsLoop( close, loop, xmlElement )
	return loop

def getManipulatorPathPluginsLoop( close, loop, xmlElement ):
	"Get loop manipulated by the plugins in the manipulator paths folder."
	manipulatorPathDictionary = xmlElement.getRootElement().xmlProcessor.manipulatorPathDictionary
	matchingPlugins = geomancer.getMatchingPlugins( manipulatorPathDictionary, xmlElement )
	for matchingPlugin in matchingPlugins:
		loop = matchingPlugin.getManipulatedPath( close, loop, xmlElement )
	return loop

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
	sidesPerRadian = 0.5 / math.pi * geomancer.getSides( sideLength, xmlElement )
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
	path = geomancer.getPathByPrefix( getSegmentPathDefault(), 'segment', xmlElement )
	if path == getSegmentPathDefault():
		return loop
	path = getXNormalizedVector3Path( path )
	segmentCenter = geomancer.getVector3ByKey( 'segmentcenter', None, xmlElement )
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
	firstElementClass = None
	if len( geometryOutput ) > 0:
		firstElementClass = geometryOutput[ 0 ].__class__
	if firstElementClass == [].__class__:
		group.convertXMLElementRenameByPaths( geometryOutput, xmlElement, xmlProcessor )
	else:
		path.convertXMLElementRename( geometryOutput, xmlElement, xmlProcessor )
	xmlProcessor.processXMLElement( xmlElement )
