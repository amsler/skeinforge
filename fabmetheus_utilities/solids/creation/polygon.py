"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.creation import lineation
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
	if '_arguments' in xmlElement.attributeDictionary:
		xmlElement.attributeDictionary[ 'sides' ] = xmlElement.attributeDictionary[ '_arguments' ][ 0 ]
	sides = geomancer.getEvaluatedFloatDefault( 4.0, 'sides', xmlElement )
	if sides == None:
		sides = 3
	sideAngle = 2.0 * math.pi / float( sides )
	radius = getRadiusFromXMLElement( sideAngle, xmlElement )
	loop = []
	sidesCeiling = int( math.ceil( abs( sides ) ) )
	start = geomancer.getEvaluatedIntZero( 'start', xmlElement )
	start = getWrappedInteger( start, sidesCeiling )
	extent = geomancer.getEvaluatedIntDefault( sidesCeiling - start, 'extent', xmlElement )
	end = geomancer.getEvaluatedIntDefault( start + extent, 'end', xmlElement )
	end = getWrappedInteger( end, sidesCeiling )
	for side in xrange( start, min( end, sidesCeiling ) ):
		angle = float( side ) * sideAngle
		point = euclidean.getWiddershinsUnitPolar( angle ) * radius
		vertex = Vector3( point.real, point.imag )
		loop.append( vertex )
	sideLength = sideAngle * radius
	return lineation.getGeometryOutputByLoop( loop, None, sideAngle, sideLength, xmlElement )

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

def getWrappedInteger( integer, modulo ):
	"Get wrapped integer."
	if integer >= modulo:
		return modulo
	if integer >= 0:
		return integer
	return integer % modulo

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	path.convertXMLElementRename( getGeometryOutput( xmlElement ), xmlElement, xmlProcessor )
	xmlProcessor.processXMLElement( xmlElement )
