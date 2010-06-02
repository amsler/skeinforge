"""
Boolean geometry array.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools import matrix4x4
from fabmetheus_utilities.solids.solid_tools import vertex
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities import euclidean


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	target = geomancer.getXMLElementByKey( 'target', xmlElement )
	if target == None:
		print( 'Warning, array could not get target.' )
		return
	verticesElement = geomancer.getXMLElementByKey( 'vertices', xmlElement )
	if verticesElement == None:
		print( 'Warning, array could not get vertices.' )
		return
	vertices = verticesElement.object.getVertices()
	arrayDictionary = xmlElement.attributeDictionary.copy()
	targetMatrix4X4Copy = matrix4x4.Matrix4X4().getFromXMLElement( target )
	matrix4x4.setAttributeDictionaryToMatrix( target.attributeDictionary, targetMatrix4X4Copy )
	xmlElement.className = 'group'
	for vector3Index in xrange( len( vertices ) ):
		vector3 = vertices[ vector3Index ]
		vector3Matrix4X4 = matrix4x4.Matrix4X4( targetMatrix4X4Copy.matrixTetragrid )
		lastChild = target.getCopy( xmlElement.getIDSuffix( vector3Index ), xmlElement )
		euclidean.overwriteDictionary( xmlElement.attributeDictionary, [ 'id' ], [ 'visible' ], lastChild.attributeDictionary )
		vertexElement = vertex.getUnboundVertexElement( vector3 )
		matrix4x4.setXMLElementMatrixToMatrixAttributeDictionary( vertexElement, vector3Matrix4X4, lastChild )
	xmlProcessor.processXMLElement( xmlElement )
