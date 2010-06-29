"""
Boolean geometry extrusion.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities.vector3index import Vector3Index
from fabmetheus_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def addLoop( endMultiplier, extrude, loopLists, path, portionDirectionIndex, portionDirections, vertices ):
	"Add an indexed loop to the vertices."
	portionDirection = portionDirections[ portionDirectionIndex ]
	if portionDirection.directionReversed == True:
		loopLists.append( [] )
	loops = loopLists[ - 1 ]
	interpolationOffset = extrude.interpolationDictionary[ 'offset' ]
	offset = interpolationOffset.getVector3ByPortion( portionDirection )
	if endMultiplier != None:
		if portionDirectionIndex == 0:
			setOffsetByMultiplier( interpolationOffset.path[ 1 ], interpolationOffset.path[ 0 ], endMultiplier, offset )
		elif portionDirectionIndex == len( portionDirections ) - 1:
			setOffsetByMultiplier( interpolationOffset.path[ - 2 ], interpolationOffset.path[ - 1 ], endMultiplier, offset )
	scale = extrude.interpolationDictionary[ 'scale' ].getComplexByPortion( portionDirection )
	twist = extrude.interpolationDictionary[ 'twist' ].getYByPortion( portionDirection )
	projectiveSpace = euclidean.ProjectiveSpace()
	if extrude.tiltTop == None:
		tilt = extrude.interpolationDictionary[ 'tilt' ].getComplexByPortion( portionDirection )
		projectiveSpace = projectiveSpace.getByTilt( tilt )
	else:
		normals = getNormals( interpolationOffset, offset, portionDirection )
		normalFirst = normals[ 0 ]
		normalAverage = getNormalAverage( normals )
		if extrude.tiltFollow and extrude.oldProjectiveSpace != None:
			projectiveSpace = extrude.oldProjectiveSpace.getNextSpace( normalAverage )
		else:
			projectiveSpace = projectiveSpace.getByBasisZTop( normalAverage, extrude.tiltTop )
		extrude.oldProjectiveSpace = projectiveSpace
		projectiveSpace.unbuckle( extrude.maximumUnbuckling, normalFirst )
	projectiveSpace = projectiveSpace.getSpaceByXYScaleAngle( twist, scale )
	loop = []
	if ( abs( projectiveSpace.basisX ) + abs( projectiveSpace.basisY ) ) < 0.0001:
		vector3Index = Vector3Index( len( vertices ) )
		addOffsetAddToLists( loop, offset, vector3Index, vertices )
		loops.append( loop )
		return
	for point in path:
		vector3Index = Vector3Index( len( vertices ) )
		projectedVertex = projectiveSpace.getVector3ByPoint( point )
		vector3Index.setToVector3( projectedVertex )
		addOffsetAddToLists( loop, offset, vector3Index, vertices )
	loops.append( loop )

def addOffsetAddToLists( loop, offset, vector3Index, vertices ):
	"Add an indexed loop to the vertices."
	vector3Index += offset
	loop.append( vector3Index )
	vertices.append( vector3Index )

def addTwistPortions( interpolationTwist, remainderPortionDirection, twistPrecision ):
	"Add twist portions."
	lastPortionDirection = interpolationTwist.portionDirections[ - 1 ]
	if remainderPortionDirection.portion == lastPortionDirection.portion:
		return
	lastTwist = interpolationTwist.getYByPortion( lastPortionDirection )
	remainderTwist = interpolationTwist.getYByPortion( remainderPortionDirection )
	twistSegments = int( math.floor( abs( remainderTwist - lastTwist ) / twistPrecision ) )
	if twistSegments < 1:
		return
	portionDifference = remainderPortionDirection.portion - lastPortionDirection.portion
	twistSegmentsPlusOne = float( twistSegments + 1 )
	for twistSegment in xrange( twistSegments ):
		additionalPortion = portionDifference * float( twistSegment + 1 ) / twistSegmentsPlusOne
		portionDirection = evaluate.PortionDirection( lastPortionDirection.portion + additionalPortion )
		interpolationTwist.portionDirections.append( portionDirection )

def getGeometryOutput( xmlElement ):
	"Get vector3 vertices from attribute dictionary."
	paths = evaluate.getPathsByKeys( [ 'crosssection', 'section', 'target' ], xmlElement )
	if len( euclidean.getConcatenatedList( paths ) ) == 0:
		print( 'Warning, in extrude there are no paths.' )
		print( xmlElement.attributeDictionary )
		return None
	offsetPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
	extrude = Extrude()
	extrude.tiltFollow = evaluate.getEvaluatedBooleanDefault( extrude.tiltFollow, 'tiltfollow', xmlElement )
	extrude.tiltTop = evaluate.getVector3ByPrefix( 'tilttop', extrude.tiltTop, xmlElement )
	extrude.maximumUnbuckling = evaluate.getEvaluatedFloatDefault( 5.0, 'maximumunbuckling', xmlElement )
	scalePathDefault = [ Vector3( 1.0, 1.0, 0.0 ), Vector3( 1.0, 1.0, 1.0 ) ]
	extrude.interpolationDictionary[ 'scale' ] = evaluate.Interpolation().getByPrefixZ( scalePathDefault, 'scale', xmlElement )
	if extrude.tiltTop == None:
		extrude.interpolationDictionary[ 'offset' ] = evaluate.Interpolation().getByPrefixZ( offsetPathDefault, '', xmlElement )
		tiltPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
		interpolationTilt = evaluate.Interpolation().getByPrefixZ( tiltPathDefault, 'tilt', xmlElement )
		extrude.interpolationDictionary[ 'tilt' ] = interpolationTilt
		for point in interpolationTilt.path:
			point.x = math.radians( point.x )
			point.y = math.radians( point.y )
	else:
		offsetAlongDefault = [ Vector3(), Vector3( 1.0, 0.0, 0.0 ) ]
		extrude.interpolationDictionary[ 'offset' ] = evaluate.Interpolation().getByPrefixAlong( offsetAlongDefault, '', xmlElement )
	insertTwistPortions( extrude.interpolationDictionary, xmlElement )
	segments = evaluate.getEvaluatedIntOne( 'segments', xmlElement )
	negatives = []
	positives = []
	portionDirections = evaluate.getSpacedPortionDirections( extrude.interpolationDictionary )
	for path in paths:
		endMultiplier = None
		if not euclidean.getIsWiddershinsByVector3( path ):
			endMultiplier = 1.000001
		geometryOutput = getGeometryOutputByPath( endMultiplier, extrude, path, portionDirections )
		if endMultiplier == None:
			positives.append( geometryOutput )
		else:
			negatives.append( geometryOutput )
	positiveOutput = trianglemesh.getUnifiedOutput( positives )
	if len( negatives ) < 1:
		return positiveOutput
	return { 'difference' : [ positiveOutput ] + negatives }

def getGeometryOutputByPath( endMultiplier, extrude, path, portionDirections ):
	"Get vector3 vertices from attribute dictionary."
	vertices = []
	loopLists = [ [] ]
	extrude.oldProjectiveSpace = None
	for portionDirectionIndex in xrange( len( portionDirections ) ):
		addLoop( endMultiplier, extrude, loopLists, path, portionDirectionIndex, portionDirections, vertices )
	return trianglemesh.getPillarsOutput( loopLists )

def getNormalAverage( normals ):
	"Get normal."
	if len( normals ) < 2:
		return normals[ 0 ]
	return ( normals[ 0 ] + normals[ 1 ] ).getNormalized()

def getNormals( interpolationOffset, offset, portionDirection ):
	"Get normals."
	normals = []
	portionFrom = portionDirection.portion - 0.0001
	portionTo = portionDirection.portion + 0.0001
	if portionFrom >= 0.0:
		normals.append( ( offset - interpolationOffset.getVector3ByPortion( evaluate.PortionDirection( portionFrom ) ) ).getNormalized() )
	if portionTo <= 1.0:
		normals.append( ( interpolationOffset.getVector3ByPortion( evaluate.PortionDirection( portionTo ) ) - offset ).getNormalized() )
	return normals

def insertTwistPortions( interpolationDictionary, xmlElement ):
	"Insert twist portions and radian the twist."
	twist = evaluate.getEvaluatedFloatZero( 'twist', xmlElement )
	twistPathDefault = [ Vector3(), Vector3( 1.0, twist ) ]
	interpolationTwist = evaluate.Interpolation().getByPrefixX( twistPathDefault, 'twist', xmlElement )
	interpolationDictionary[ 'twist' ] = interpolationTwist
	for point in interpolationTwist.path:
		point.y = math.radians( point.y )
	remainderPortionDirections = interpolationTwist.portionDirections[ 1 : ]
	interpolationTwist.portionDirections = [ interpolationTwist.portionDirections[ 0 ] ]
	twistPrecision = math.radians( xmlElement.getCascadeFloat( 5.0, 'twistprecision' ) )
	for remainderPortionDirection in remainderPortionDirections:
		addTwistPortions( interpolationTwist, remainderPortionDirection, twistPrecision )
		interpolationTwist.portionDirections.append( remainderPortionDirection )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	geometryOutput = getGeometryOutput( xmlElement )
	if geometryOutput == None:
		return
	xmlProcessor.convertXMLElement( geometryOutput, xmlElement )
	xmlProcessor.processXMLElement( xmlElement )

def setOffsetByMultiplier( begin, end, multiplier, offset ):
	"Set the offset by the multiplier."
	return
	segment = end - begin
	delta = segment * multiplier - segment
	offset.setToVector3( offset + delta )


class Extrude:
	"Class to hold extrude variables."
	def __init__( self ):
		self.interpolationDictionary = {}
		self.tiltFollow = True
		self.tiltTop = None

	def __repr__( self ):
		"Get the string representation of extrude."
		return '%s, %s' % ( self.interpolationDictionary, self.tiltTop )
