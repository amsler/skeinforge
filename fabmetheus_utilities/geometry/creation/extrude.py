"""
Boolean geometry extrusion.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import solid
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
	interpolationOffset = extrude.interpolationDictionary['offset']
	offset = interpolationOffset.getVector3ByPortion( portionDirection )
	if endMultiplier != None:
		if portionDirectionIndex == 0:
			setOffsetByMultiplier( interpolationOffset.path[1], interpolationOffset.path[0], endMultiplier, offset )
		elif portionDirectionIndex == len( portionDirections ) - 1:
			setOffsetByMultiplier( interpolationOffset.path[ - 2 ], interpolationOffset.path[ - 1 ], endMultiplier, offset )
	scale = extrude.interpolationDictionary['scale'].getComplexByPortion( portionDirection )
	twist = extrude.interpolationDictionary['twist'].getYByPortion( portionDirection )
	projectiveSpace = euclidean.ProjectiveSpace()
	if extrude.tiltTop == None:
		tilt = extrude.interpolationDictionary['tilt'].getComplexByPortion( portionDirection )
		projectiveSpace = projectiveSpace.getByTilt( tilt )
	else:
		normals = getNormals( interpolationOffset, offset, portionDirection )
		normalFirst = normals[0]
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
		loops.append(loop)
		return
	for point in path:
		vector3Index = Vector3Index( len( vertices ) )
		projectedVertex = projectiveSpace.getVector3ByPoint( point )
		vector3Index.setToVector3( projectedVertex )
		addOffsetAddToLists( loop, offset, vector3Index, vertices )
	loops.append(loop)

def addOffsetAddToLists( loop, offset, vector3Index, vertices ):
	"Add an indexed loop to the vertices."
	vector3Index += offset
	loop.append( vector3Index )
	vertices.append( vector3Index )

def addSpacedPortionDirection( portionDirection, spacedPortionDirections ):
	"Add spaced portion directions."
	lastSpacedPortionDirection = spacedPortionDirections[ - 1 ]
	if portionDirection.portion - lastSpacedPortionDirection.portion > 0.003:
		spacedPortionDirections.append( portionDirection )
		return
	if portionDirection.directionReversed > lastSpacedPortionDirection.directionReversed:
		spacedPortionDirections.append( portionDirection )

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
		portionDirection = PortionDirection( lastPortionDirection.portion + additionalPortion )
		interpolationTwist.portionDirections.append( portionDirection )

def comparePortionDirection( portionDirection, otherPortionDirection ):
	"Comparison in order to sort portion directions in ascending order of portion then direction."
	if portionDirection.portion > otherPortionDirection.portion:
		return 1
	if portionDirection.portion < otherPortionDirection.portion:
		return - 1
	if portionDirection.directionReversed < otherPortionDirection.directionReversed:
		return - 1
	return portionDirection.directionReversed > otherPortionDirection.directionReversed

def getGeometryOutput(xmlElement):
	"Get triangle mesh from attribute dictionary."
	paths = evaluate.getPathsByKeys( ['crosssection', 'section', 'target'], xmlElement )
	if len( euclidean.getConcatenatedList( paths ) ) == 0:
		print('Warning, in extrude there are no paths.')
		print( xmlElement.attributeDictionary )
		return None
	offsetPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
	extrude = Extrude()
	extrude.tiltFollow = evaluate.getEvaluatedBooleanDefault( extrude.tiltFollow, 'tiltfollow', xmlElement )
	extrude.tiltTop = evaluate.getVector3ByPrefix('tilttop', extrude.tiltTop, xmlElement )
	extrude.maximumUnbuckling = evaluate.getEvaluatedFloatDefault( 5.0, 'maximumunbuckling', xmlElement )
	scalePathDefault = [ Vector3( 1.0, 1.0, 0.0 ), Vector3( 1.0, 1.0, 1.0 ) ]
	extrude.interpolationDictionary['scale'] = Interpolation().getByPrefixZ( scalePathDefault, 'scale', xmlElement )
	if extrude.tiltTop == None:
		extrude.interpolationDictionary['offset'] = Interpolation().getByPrefixZ( offsetPathDefault, '', xmlElement )
		tiltPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
		interpolationTilt = Interpolation().getByPrefixZ( tiltPathDefault, 'tilt', xmlElement )
		extrude.interpolationDictionary['tilt'] = interpolationTilt
		for point in interpolationTilt.path:
			point.x = math.radians( point.x )
			point.y = math.radians( point.y )
	else:
		offsetAlongDefault = [ Vector3(), Vector3( 1.0, 0.0, 0.0 ) ]
		extrude.interpolationDictionary['offset'] = Interpolation().getByPrefixAlong( offsetAlongDefault, '', xmlElement )
	insertTwistPortions( extrude.interpolationDictionary, xmlElement )
	segments = evaluate.getEvaluatedIntOne('segments', xmlElement )
	negatives = []
	positives = []
	portionDirections = getSpacedPortionDirections( extrude.interpolationDictionary )
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
	interpolationOffset = extrude.interpolationDictionary['offset']
	if len( negatives ) < 1:
		return getGeometryOutputWithConnection( positiveOutput, interpolationOffset, xmlElement )
	return getGeometryOutputWithConnection( { 'difference' : [ positiveOutput ] + negatives }, interpolationOffset, xmlElement )

def getGeometryOutputByArguments(arguments, xmlElement):
	"Get triangle mesh from attribute dictionary by arguments."
	return getGeometryOutput(xmlElement)

def getGeometryOutputByPath( endMultiplier, extrude, path, portionDirections ):
	"Get vector3 vertices from attribute dictionary."
	vertices = []
	loopLists = [ [] ]
	extrude.oldProjectiveSpace = None
	for portionDirectionIndex in xrange( len( portionDirections ) ):
		addLoop( endMultiplier, extrude, loopLists, path, portionDirectionIndex, portionDirections, vertices )
	return trianglemesh.getPillarsOutput( loopLists )

def getGeometryOutputWithConnection( geometryOutput, interpolationOffset, xmlElement ):
	"Get solid output with connection attributes."
	geometryOutputValues = geometryOutput.values()
	if len( geometryOutputValues ) < 1:
		return geometryOutput
	firstValue = geometryOutputValues[0]
	firstValue['connectionfrom'] = interpolationOffset.getVector3ByPortion( PortionDirection( 0.0 ) )
	firstValue['connectionto'] = interpolationOffset.getVector3ByPortion( PortionDirection( 1.0 ) )
	return solid.getGeometryOutputByManipulation( geometryOutput, xmlElement )

def getNormalAverage( normals ):
	"Get normal."
	if len( normals ) < 2:
		return normals[0]
	return ( normals[0] + normals[1] ).getNormalized()

def getNormals( interpolationOffset, offset, portionDirection ):
	"Get normals."
	normals = []
	portionFrom = portionDirection.portion - 0.0001
	portionTo = portionDirection.portion + 0.0001
	if portionFrom >= 0.0:
		normals.append( ( offset - interpolationOffset.getVector3ByPortion( PortionDirection( portionFrom ) ) ).getNormalized() )
	if portionTo <= 1.0:
		normals.append( ( interpolationOffset.getVector3ByPortion( PortionDirection( portionTo ) ) - offset ).getNormalized() )
	return normals

def getSpacedPortionDirections( interpolationDictionary ):
	"Get sorted portion directions."
	portionDirections = []
	for interpolationDictionaryValue in interpolationDictionary.values():
		portionDirections += interpolationDictionaryValue.portionDirections
	portionDirections.sort( comparePortionDirection )
	if len( portionDirections ) < 1:
		return []
	spacedPortionDirections = [ portionDirections[0] ]
	for portionDirection in portionDirections[ 1 : ]:
		addSpacedPortionDirection( portionDirection, spacedPortionDirections )
	return spacedPortionDirections

def insertTwistPortions( interpolationDictionary, xmlElement ):
	"Insert twist portions and radian the twist."
	twist = evaluate.getEvaluatedFloatZero('twist', xmlElement )
	twistPathDefault = [ Vector3(), Vector3( 1.0, twist ) ]
	interpolationTwist = Interpolation().getByPrefixX( twistPathDefault, 'twist', xmlElement )
	interpolationDictionary['twist'] = interpolationTwist
	for point in interpolationTwist.path:
		point.y = math.radians( point.y )
	remainderPortionDirections = interpolationTwist.portionDirections[ 1 : ]
	interpolationTwist.portionDirections = [ interpolationTwist.portionDirections[0] ]
	twistPrecision = math.radians( xmlElement.getCascadeFloat( 5.0, 'twistprecision') )
	for remainderPortionDirection in remainderPortionDirections:
		addTwistPortions( interpolationTwist, remainderPortionDirection, twistPrecision )
		interpolationTwist.portionDirections.append( remainderPortionDirection )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	geometryOutput = getGeometryOutput(xmlElement)
	if geometryOutput == None:
		return
	xmlProcessor.convertXMLElement( geometryOutput, xmlElement )
	xmlProcessor.processXMLElement(xmlElement)

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


class Interpolation:
	"Class to interpolate a path."
	def __init__( self ):
		"Set index."
		self.interpolationIndex = 0

	def getByDistances( self ):
		"Get by distances."
		beginDistance = self.distances[0]
		self.interpolationLength = self.distances[ - 1 ] - beginDistance
		self.close = abs( 0.000001 * self.interpolationLength )
		self.portionDirections = []
		oldDistance = beginDistance - self.interpolationLength
		for distance in self.distances:
			portionDirection = PortionDirection( distance / self.interpolationLength )
			if abs( distance - oldDistance ) < self.close:
				portionDirection.directionReversed = True
			self.portionDirections.append( portionDirection )
			oldDistance = distance
		return self

	def getByPrefixAlong( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element along the path."
		if len( path ) < 2:
			print('Warning, path is too small in evaluate in Interpolation.')
			return
		self.path = evaluate.getPathByPrefix( path, prefix, xmlElement )
		self.distances = [ 0.0 ]
		previousPoint = self.path[0]
		for point in self.path[ 1 : ]:
			distanceDifference = abs( point - previousPoint )
			self.distances.append( self.distances[ - 1 ] + distanceDifference )
			previousPoint = point
		return self.getByDistances()

	def getByPrefixX( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element in the z direction."
		if len( path ) < 2:
			print('Warning, path is too small in evaluate in Interpolation.')
			return
		self.path = evaluate.getPathByPrefix( path, prefix, xmlElement )
		self.distances = []
		for point in self.path:
			self.distances.append( point.x )
		return self.getByDistances()

	def getByPrefixZ( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element in the z direction."
		if len( path ) < 2:
			print('Warning, path is too small in evaluate in Interpolation.')
			return
		self.path = evaluate.getPathByPrefix( path, prefix, xmlElement )
		self.distances = []
		for point in self.path:
			self.distances.append( point.z )
		return self.getByDistances()

	def getComparison( self, first, second ):
		"Compare the first with the second."
		if abs( second - first ) < self.close:
			return 0
		if second > first:
			return 1
		return - 1

	def getComplexByPortion( self, portionDirection ):
		"Get complex from z portion."
		self.setInterpolationIndexFromTo( portionDirection )
		return self.oneMinusInnerPortion * self.fromVertex.dropAxis( 2 ) + self.innerPortion * self.toVertex.dropAxis( 2 )

	def getInnerPortion( self ):
		"Get inner x portion."
		fromDistance = self.distances[ self.interpolationIndex ]
		innerLength = self.distances[ self.interpolationIndex + 1 ] - fromDistance
		if abs( innerLength ) == 0.0:
			return 0.0
		return ( self.absolutePortion - fromDistance ) / innerLength

	def getVector3ByPortion( self, portionDirection ):
		"Get vector3 from z portion."
		self.setInterpolationIndexFromTo( portionDirection )
		return self.oneMinusInnerPortion * self.fromVertex + self.innerPortion * self.toVertex

	def getYByPortion( self, portionDirection ):
		"Get y from x portion."
		self.setInterpolationIndexFromTo( portionDirection )
		return self.oneMinusInnerPortion * self.fromVertex.y + self.innerPortion * self.toVertex.y

	def setInterpolationIndex( self, portionDirection ):
		"Set the interpolation index."
		self.absolutePortion = self.distances[0] + self.interpolationLength * portionDirection.portion
		interpolationIndexes = range( 0, len( self.distances ) - 1 )
		if portionDirection.directionReversed:
			interpolationIndexes.reverse()
		for self.interpolationIndex in interpolationIndexes:
			begin = self.distances[ self.interpolationIndex ]
			end = self.distances[ self.interpolationIndex + 1 ]
			if self.getComparison( begin, self.absolutePortion ) != self.getComparison( end, self.absolutePortion ):
				return

	def setInterpolationIndexFromTo( self, portionDirection ):
		"Set the interpolation index, the from vertex and the to vertex."
		self.setInterpolationIndex( portionDirection )
		self.innerPortion = self.getInnerPortion()
		self.oneMinusInnerPortion = 1.0 - self.innerPortion
		self.fromVertex = self.path[ self.interpolationIndex ]
		self.toVertex = self.path[ self.interpolationIndex + 1 ]


class PortionDirection:
	"Class to hold a portion and direction."
	def __init__( self, portion ):
		"Initialize."
		self.directionReversed = False
		self.portion = portion

	def __repr__( self ):
		"Get the string representation of this PortionDirection."
		return '%s: %s' % ( self.portion, self.directionReversed )
