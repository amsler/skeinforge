"""
Boolean geometry translation.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation_tools import solid
from fabmetheus_utilities.geometry.manipulation_evaluator_tools import matrix
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


globalExecutionOrder = 380


def getManipulatedPaths( close, loop, prefix, sideLength, xmlElement ):
	"Get equated paths."
	translatePoints( loop, prefix, xmlElement )
	return [ loop ]

def getManipulatedGeometryOutput( geometryOutput, xmlElement ):
	"Get equated geometryOutput."
	translatePoints( matrix.getConnectionVertices( geometryOutput ), 'translate.', xmlElement )
	return geometryOutput

def manipulateXMLElement(target, xmlElement, xmlProcessor):
	"Manipulate the xml element."
	translateVector3 = matrix.getCumulativeVector3( '', Vector3(), xmlElement )
	if abs( translateVector3 ) <= 0.0:
		print( 'Warning, translateVector3 was zero in translate so nothing will be done for:' )
		print( xmlElement )
		return
	targetMatrix = matrix.getFromObjectOrXMLElement(target)
	targetMatrix.matrixTetragrid = matrix.getIdentityMatrixTetragrid(targetMatrix.matrixTetragrid)
	targetMatrix.matrixTetragrid[ 0 ][ 3 ] += translateVector3.x
	targetMatrix.matrixTetragrid[ 1 ][ 3 ] += translateVector3.y
	targetMatrix.matrixTetragrid[ 2 ][ 3 ] += translateVector3.z
	matrix.setAttributeDictionaryMatrixToMatrix( targetMatrix, target )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	solid.processXMLElementByFunction( manipulateXMLElement, xmlElement, xmlProcessor )

def translatePoints( points, prefix, xmlElement ):
	"Translate the points."
	translateVector3 = matrix.getCumulativeVector3(prefix, Vector3(), xmlElement)
	if abs(translateVector3) <= 0.0:
		return
	for point in points:
		point.setToVector3(point + translateVector3)
