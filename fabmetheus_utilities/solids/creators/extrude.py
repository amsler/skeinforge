"""
Boolean geometry extrusion.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities.vector3index import Vector3Index
from fabmetheus_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def addLoop( loops, offset, originVertices, scale, tilt, twistRadians, vertices ):
	"Add an indexed loop to the vertices."
	loop = []
	planeAngle = euclidean.getWiddershinsUnitPolar( twistRadians )
	if abs( scale ) < 0.0001:
		vector3Index = Vector3Index( len( vertices ) )
		addOffsetAddToLists( loop, offset, vector3Index, vertices )
		loops.append( loop )
		return
	for originVertex in originVertices:
		vector3Index = Vector3Index( len( vertices ) )
		scaledOriginVertex = Vector3( originVertex.x * scale.real, originVertex.y * scale.imag, originVertex.z )
		vertexXZ = complex( scaledOriginVertex.x, scaledOriginVertex.z )
		vertexYZ = complex( scaledOriginVertex.y, scaledOriginVertex.z )
		tiltDeltaXZ = vertexXZ * getTiltPlaneAngle( tilt.real )
		tiltDeltaYZ = vertexYZ * getTiltPlaneAngle( tilt.imag )
		scaledOriginVertex.x += tiltDeltaXZ.real
		scaledOriginVertex.y += tiltDeltaYZ.real
		scaledOriginVertex.z += tiltDeltaXZ.imag + tiltDeltaYZ.imag
		vector3Index.setToVector3( euclidean.getRoundZAxisByPlaneAngle( planeAngle, scaledOriginVertex ) )
		addOffsetAddToLists( loop, offset, vector3Index, vertices )
	loops.append( loop )

def addOffsetAddToLists( loop, offset, vector3Index, vertices ):
	"Add an indexed loop to the vertices."
	vector3Index += offset
	loop.append( vector3Index )
	vertices.append( vector3Index )

def getGeometryOutput( xmlElement ):
	"Get vector3 vertices from attribute dictionary."
	paths = geomancer.getPathsByKey( 'target', xmlElement )
	if len( paths ) == 0:
		print( 'Warning, in extrude there are no paths.' )
		print( xmlElement.attributeDictionary )
		return None
	offsetPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
	interpolationOffset = geomancer.Interpolation().getByPrefixZ( offsetPathDefault, '', xmlElement )
	scalePathDefault = [ Vector3( 1.0, 1.0, 0.0 ), Vector3( 1.0, 1.0, 1.0 ) ]
	interpolationScale = geomancer.Interpolation().getByPrefixZ( scalePathDefault, 'scale', xmlElement )
	tiltPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
	interpolationTilt = geomancer.Interpolation().getByPrefixZ( tiltPathDefault, 'tilt', xmlElement )
	segments = geomancer.getEvaluatedIntOne( 'segments', xmlElement )
	twist = geomancer.getEvaluatedFloatZero( 'twist', xmlElement )
	twistPathDefault = [ Vector3(), Vector3( 1.0, twist ) ]
	interpolationTwist = geomancer.Interpolation().getByPrefixX( twistPathDefault, 'twist', xmlElement )
	negatives = []
	positives = []
	portionDirections = interpolationOffset.portionDirections
	for path in paths:
		endMultiplier = None
		if not euclidean.getIsWiddershinsByVector3( path ):
			endMultiplier = 1.000001
		geometryOutput = getGeometryOutputByPath( endMultiplier, interpolationOffset, interpolationScale, interpolationTilt, interpolationTwist, path, portionDirections )
		if endMultiplier == None:
			positives.append( geometryOutput )
		else:
			negatives.append( geometryOutput )
	positiveOutput = getPositiveOutput( positives )
	if len( negatives ) < 1:
		return positiveOutput
	return { 'difference' : [ positiveOutput ] + negatives }

def getGeometryOutputByPath( endMultiplier, interpolationOffset, interpolationScale, interpolationTilt, interpolationTwist, path, portionDirections ):
	"Get vector3 vertices from attribute dictionary."
	vertices = []
	loops = []
	for portionDirection in portionDirections:
		portion = portionDirection.portion
		offset = interpolationOffset.getVector3ByZPortion( portion )
		if endMultiplier != None:
			if portionDirection == portionDirections[ 0 ]:
				setOffsetByMultiplier( interpolationOffset.path[ 1 ], interpolationOffset.path[ 0 ], endMultiplier, offset )
			elif portionDirection == portionDirections[ - 1 ]:
				setOffsetByMultiplier( interpolationOffset.path[ - 2 ], interpolationOffset.path[ - 1 ], endMultiplier, offset )
		scale = interpolationScale.getComplexByZPortion( portion )
		tilt = interpolationTilt.getComplexByZPortion( portion )
		twistRadians = math.radians( interpolationTwist.getYByXPortion( portion ) )
		addLoop( loops, offset, path, scale, tilt, twistRadians, vertices )
	faces = []
	trianglemesh.addPillarFromConvexLoops( faces, loops )
	return { 'trianglemesh' : { 'vertex' : vertices, 'face' : faces } }

def getPositiveOutput( positives ):
	"Get vector3 vertices from attribute dictionary."
	if len( positives ) < 1:
		return { 'trianglemesh' : { 'vertex' : [], 'face' : [] } }
	if len( positives ) < 2:
		return positives[ 0 ]
	return { 'union' : positives }

def getTiltPlaneAngle( tiltScalar ):
	"Get the tilt plane angle."
	return euclidean.getWiddershinsUnitPolar( math.radians( tiltScalar ) ) - complex( 1.0, 0.0 )

def processXMLElement( xmlElement ):
	"Process the xml element."
	geometryOutput = getGeometryOutput( xmlElement )
	if geometryOutput == None:
		return
	xmlElement.getRootElement().xmlProcessor.convertXMLElement( geometryOutput, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processXMLElement( xmlElement )

def setOffsetByMultiplier( begin, end, multiplier, offset ):
	"Set the offset by the multiplier."
	return
	segment = end - begin
	delta = segment * multiplier - segment
	offset.setToVector3( offset + delta )
