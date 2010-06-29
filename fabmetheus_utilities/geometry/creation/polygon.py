"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import lineation
from fabmetheus_utilities.geometry.geometry_tools import path
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
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
		arguments = xmlElement.attributeDictionary[ '_arguments' ]
		if len( arguments ) > 0:
			xmlElement.attributeDictionary[ 'sides' ] = arguments[ 0 ]
	sides = evaluate.getEvaluatedFloatDefault( 4.0, 'sides', xmlElement )
	sideAngle = 2.0 * math.pi / float( sides )
	radiusXY = evaluate.RadiusXY().getByRadius( getRadiusFromXMLElement( sideAngle, xmlElement ), xmlElement )
	loop = []
	sidesCeiling = int( math.ceil( abs( sides ) ) )
	start = evaluate.getEvaluatedIntZero( 'start', xmlElement )
	start = getWrappedInteger( start, sidesCeiling )
	extent = evaluate.getEvaluatedIntDefault( sidesCeiling - start, 'extent', xmlElement )
	end = evaluate.getEvaluatedIntDefault( start + extent, 'end', xmlElement )
	end = getWrappedInteger( end, sidesCeiling )
	for side in xrange( start, min( end, sidesCeiling ) ):
		angle = float( side ) * sideAngle
		point = euclidean.getWiddershinsUnitPolar( angle )
		vertex = Vector3( point.real * radiusXY.radiusX, point.imag * radiusXY.radiusY )
		loop.append( vertex )
	sideLength = sideAngle * radiusXY.radius
	return lineation.getGeometryOutputByLoop( None, lineation.SideLoop( loop, sideAngle, sideLength ), xmlElement )

def getRadiusFromApothem( apothem, sideAngle ):
	"Get radius from apothem."
	return apothem / math.cos( 0.5 * sideAngle )

def getRadiusFromXMLElement( sideAngle, xmlElement ):
	"Get radius from attribute dictionary."
	if 'radius' in xmlElement.attributeDictionary:
		return evaluate.getEvaluatedFloatOne( 'radius', xmlElement )
	if 'apothem' in xmlElement.attributeDictionary:
		return getRadiusFromApothem( evaluate.getEvaluatedFloatOne( 'apothem', xmlElement ), sideAngle )
	if 'inradius' in xmlElement.attributeDictionary:
		return getRadiusFromApothem( evaluate.getEvaluatedFloatOne( 'inradius', xmlElement ), sideAngle )
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
	lineation.processXMLElementByGeometry( getGeometryOutput( xmlElement ), xmlElement, xmlProcessor )
