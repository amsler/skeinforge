"""
Square path.

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
	halfX = 1.0
	halfX = geomancer.getEvaluatedFloatDefault( halfX, 'halfx', xmlElement )
	halfX = 0.5 * geomancer.getEvaluatedFloatDefault( halfX / 0.5, 'width', xmlElement )
	bottomHalfX = geomancer.getEvaluatedFloatDefault( halfX, 'bottomhalfx', xmlElement )
	bottomHalfX = 0.5 * geomancer.getEvaluatedFloatDefault( halfX / 0.5, 'bottomwidth', xmlElement )
	topHalfX = geomancer.getEvaluatedFloatDefault( halfX, 'tophalfx', xmlElement )
	topHalfX = 0.5 * geomancer.getEvaluatedFloatDefault( halfX / 0.5, 'topwidth', xmlElement )
	halfY = halfX
	if '_arguments' in xmlElement.attributeDictionary:
		arguments = xmlElement.attributeDictionary[ '_arguments' ]
		halfX = 0.5 * euclidean.getFloatFromValue( arguments[ 0 ] )
		xmlElement.attributeDictionary[ 'halfX' ] = str( halfX )
		if len( arguments ) > 1:
			halfY = 0.5 * euclidean.getFloatFromValue( arguments[ 1 ] )
		else:
			halfY = halfX
	halfY = geomancer.getEvaluatedFloatDefault( halfY, 'halfy', xmlElement )
	halfY = 0.5 * geomancer.getEvaluatedFloatDefault( halfY / 0.5, 'height', xmlElement )
	interiorAngle = geomancer.getEvaluatedFloatDefault( 90.0, 'interiorangle', xmlElement )
	topRight = complex( topHalfX, halfY )
	topLeft = complex( - topHalfX, halfY )
	bottomLeft = complex( - bottomHalfX, - halfY )
	bottomRight = complex( bottomHalfX, - halfY )
	if interiorAngle != 90.0:
		interiorPlaneAngle = euclidean.getWiddershinsUnitPolar( math.radians( interiorAngle - 90.0 ) )
		topRight = ( topRight - bottomRight ) * interiorPlaneAngle + bottomRight
		topLeft = ( topLeft - bottomLeft ) * interiorPlaneAngle + bottomLeft
	loop = [
		Vector3( topRight.real, topRight.imag ),
		Vector3( topLeft.real, topLeft.imag ),
		Vector3( bottomLeft.real, bottomLeft.imag ),
		Vector3( bottomRight.real, bottomRight.imag ) ]
	return lineation.getGeometryOutputByLoop( loop, None, 0.5 * math.pi, None, xmlElement )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	path.convertXMLElementRename( getGeometryOutput( xmlElement ), xmlElement, xmlProcessor )
	xmlProcessor.processXMLElement( xmlElement )
