"""
Face of a triangle mesh.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools import path
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getGeometryOutput( xmlElement ):
	"Get vector3 vertices from attribute dictionary."
	if '__list__' in xmlElement.attributeDictionary:
		xmlElement.attributeDictionary[ 'sides' ] = xmlElement.attributeDictionary[ '__list__' ][ 0 ]
	sides = geomancer.getEvaluatedFloatDefault( 4.0, 'sides', xmlElement )
	if sides == None:
		sides = 3
	sideAngle = 2.0 * math.pi / float( sides )
	radius = getRadiusFromXMLElement( sideAngle, xmlElement )
	vertices = []
	for side in xrange( int( math.ceil( sides ) ) ):
		angle = float( side ) * sideAngle
		pointComplex = euclidean.getWiddershinsUnitPolar( angle ) * radius
		vertex = Vector3( pointComplex.real, pointComplex.imag )
		vertices.append( vertex )
	return vertices

def getRadiusFromApothem( apothem, sideAngle ):
	"Get radius from apothem."
	return apothem / math.cos( 0.5 * sideAngle )

def getRadiusFromXMLElement( sideAngle, xmlElement ):
	"Get radius from attribute dictionary."
	if 'radius' in xmlElement.attributeDictionary:
		return geomancer.getEvaluatedFloatOne( 'radius', xmlElement )
	if 'apothem' in xmlElement.attributeDictionary:
		return getRadiusFromApothem( geomancer.getEvaluatedFloatOne( 'apothem', xmlElement ), sideAngle )
	if 'inradius' in xmlElement.attributeDictionary:
		return getRadiusFromApothem( geomancer.getEvaluatedFloatOne( 'inradius', xmlElement ), sideAngle )
	return 1.0

def processXMLElement( xmlElement ):
	"Process the xml element."
	geometryOutput = getGeometryOutput( xmlElement )
	path.convertXMLElementRename( geometryOutput, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processXMLElement( xmlElement )
