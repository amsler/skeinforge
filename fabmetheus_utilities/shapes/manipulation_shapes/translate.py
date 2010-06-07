"""
Boolean geometry translation.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.shapes.solid_tools import matrix4x4
from fabmetheus_utilities.shapes.solid_utilities import geomancer
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getManipulatedPaths( close, loop, prefix, xmlElement ):
	"Get translated path."
	delta = geomancer.getVector3ByPrefix( prefix + 'delta', Vector3(), xmlElement )
	if abs( delta ) <= 0.0:
		return [ loop ]
	for point in loop:
		point.setToVector3( point + delta )
	return [ loop ]

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	delta = geomancer.getVector3ByPrefix( 'delta', Vector3(), xmlElement )
	if abs( delta ) <= 0.0:
		'Warning, delta was zero in translate so nothing will be done for:'
		print( xmlElement )
		return
	target = geomancer.getXMLElementByKey( 'target', xmlElement )
	if target == None:
		print( 'Warning, translate could not get target for:' )
		print( xmlElement )
		return
	targetMatrix4X4 = matrix4x4.Matrix4X4().getFromXMLElement( target )
	targetMatrix4X4.matrixTetragrid[ 0 ][ 3 ] += delta.x
	targetMatrix4X4.matrixTetragrid[ 1 ][ 3 ] += delta.y
	targetMatrix4X4.matrixTetragrid[ 2 ][ 3 ] += delta.z
	matrix4x4.setAttributeDictionaryToMatrix( target.attributeDictionary, targetMatrix4X4 )
	if target.object != None:
		target.object.matrix4X4 = targetMatrix4X4
