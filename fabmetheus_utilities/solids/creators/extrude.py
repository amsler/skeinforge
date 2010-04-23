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

def getTiltPlaneAngle( tiltScalar ):
	"Get the tilt plane angle."
	return euclidean.getWiddershinsUnitPolar( math.radians( tiltScalar ) ) - complex( 1.0, 0.0 )

def getGeometryOutput( xmlElement ):
	"Get vector3 vertices from attribute dictionary."
	paths = geomancer.getPathsByKey( 'target', xmlElement )
	if len( paths ) == 0:
		print( 'Warning, in extrude there are no paths.' )
		print( xmlElement.attributeDictionary )
		return None
	offsetPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
	interpolationOffset = geomancer.Interpolation().getByPrefix( offsetPathDefault, '', xmlElement )
	scalePathDefault = [ Vector3( 1.0, 1.0, 0.0 ), Vector3( 1.0, 1.0, 1.0 ) ]
	interpolationScale = geomancer.Interpolation().getByPrefix( scalePathDefault, 'scale', xmlElement )
	tiltPathDefault = [ Vector3(), Vector3( 0.0, 0.0, 1.0 ) ]
	interpolationTilt = geomancer.Interpolation().getByPrefix( tiltPathDefault, 'tilt', xmlElement )
	segments = geomancer.getEvaluatedIntOne( 'segments', xmlElement )
	twist = geomancer.getEvaluatedFloatZero( 'twist', xmlElement )
	twistPathDefault = [ Vector3(), Vector3( 1.0, twist ) ]
	interpolationTwist = geomancer.Interpolation().getByPrefix( twistPathDefault, 'twist', xmlElement )
	geometryOutputs = []
	for path in paths:
		geometryOutput = getGeometryOutputByPath( interpolationOffset, interpolationScale, interpolationTilt, interpolationTwist, path, segments )
		geometryOutputs.append( geometryOutput )
	return geometryOutputs[ 0 ]

def getGeometryOutputByPath( interpolationOffset, interpolationScale, interpolationTilt, interpolationTwist, path, segments ):
	"Get vector3 vertices from attribute dictionary."
	vertices = []
	loops = []
	for segmentIndex in xrange( 0, segments + 1 ):
		portion = float( segmentIndex ) / float( segments )
		scale = interpolationScale.getComplexByZPortion( portion )
		tilt = interpolationTilt.getComplexByZPortion( portion )
		twistRadians = math.radians( interpolationTwist.getYByXPortion( portion ) )
		addLoop( loops, interpolationOffset.getVector3ByZPortion( portion ), path, scale, tilt, twistRadians, vertices )
	faces = []
	trianglemesh.addPillarFromConvexLoops( faces, loops )
	return { 'trianglemesh' : { 'vertex' : vertices, 'face' : faces } }

def processXMLElement( xmlElement ):
	"Process the xml element."
	geometryOutput = getGeometryOutput( xmlElement )
	if geometryOutput == None:
		return
	xmlElement.getRootElement().xmlProcessor.convertXMLElement( geometryOutput, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processXMLElement( xmlElement )
