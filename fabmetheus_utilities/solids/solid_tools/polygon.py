"""
Face of a triangle mesh.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import xml_simple_parser
from fabmetheus_utilities import euclidean
from fabmetheus_utilities.vector3 import Vector3
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def convertPolygonElementToPathElement( vertices, xmlElement ):
	"Convert the polygon xml element to a path xml element."
	xmlElement.className = 'path'
	for vertex in vertices:
		vertexElement = xml_simple_parser.XMLElement()
		vertex.addToAttributeDictionary( vertexElement.attributeDictionary )
		vertexElement.className = 'vertex'
		vertexElement.parent = xmlElement
		xmlElement.children.append( vertexElement )

def getRadiusFromApothem( apothem, sideAngle ):
	"Get radius from apothem."
	return apothem / math.cos( 0.5 * sideAngle )

def getRadiusFromAttributeDictionary( attributeDictionary, sideAngle ):
	"Get radius from attribute dictionary."
	if 'radius' in attributeDictionary:
		return float( attributeDictionary[ 'radius' ] )
	if 'apothem' in attributeDictionary:
		return getRadiusFromApothem( float( attributeDictionary[ 'apothem' ] ), sideAngle )
	if 'inradius' in attributeDictionary:
		return getRadiusFromApothem( float( attributeDictionary[ 'inradius' ] ), sideAngle )
	return 1.0

def getVerticesFromAttributeDictionary( attributeDictionary ):
	"Get vector3 vertices from attribute dictionary."
	sides = 3
	if 'sides' in attributeDictionary:
		sides = int( attributeDictionary[ 'sides' ] )
	sideAngle = 2.0 * math.pi / float( sides )
	radius = getRadiusFromAttributeDictionary( attributeDictionary, sideAngle )
	vertices = []
	for side in xrange( sides ):
		angle = float( side ) * sideAngle
		pointComplex = euclidean.getWiddershinsUnitPolar( angle ) * radius
		vertex = Vector3( pointComplex.real, pointComplex.imag )
		vertices.append( vertex )
	return vertices

def processXMLElement( xmlElement ):
	"Process the xml element."
	vertices = getVerticesFromAttributeDictionary( xmlElement.attributeDictionary )
	convertPolygonElementToPathElement( vertices, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processXMLElement( xmlElement )
