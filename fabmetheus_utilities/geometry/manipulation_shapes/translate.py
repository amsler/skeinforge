"""
Boolean geometry translation.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_tools import matrix4x4
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getExecutionOrder():
	"Get the execution order."
	return 380

def getManipulatedPaths( close, loop, prefix, xmlElement ):
	"Get translated path."
	delta = evaluate.getVector3ByPrefix( prefix + 'delta', Vector3(), xmlElement )
	if abs( delta ) <= 0.0:
		return [ loop ]
	for point in loop:
		point.setToVector3( point + delta )
	return [ loop ]

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	delta = evaluate.getVector3ByPrefix( 'delta', Vector3(), xmlElement )
	if abs( delta ) <= 0.0:
		'Warning, delta was zero in translate so nothing will be done for:'
		print( xmlElement )
		return
	target = evaluate.getXMLElementByKey( 'target', xmlElement )
	if target == None:
		print( 'Warning, translate could not get target for:' )
		print( xmlElement )
		return
	targetMatrix4X4 = matrix4x4.Matrix4X4().getFromXMLElement( target )
	targetMatrix4X4.matrixTetragrid[ 0 ][ 3 ] += delta.x
	targetMatrix4X4.matrixTetragrid[ 1 ][ 3 ] += delta.y
	targetMatrix4X4.matrixTetragrid[ 2 ][ 3 ] += delta.z
	matrix4x4.setAttributeDictionaryMatrixToMatrix( targetMatrix4X4, target )
