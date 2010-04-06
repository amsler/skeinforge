"""
Boolean geometry array.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools import matrix4x4
from fabmetheus_utilities import euclidean


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement ):
	"Process the xml element."
	if 'target' not in xmlElement.attributeDictionary:
		return
	if 'vertices' not in xmlElement.attributeDictionary:
		return
	targetID = xmlElement.attributeDictionary[ 'target' ]
	target = xmlElement.getRootElement().idDictionary[ targetID ]
	verticesID = xmlElement.attributeDictionary[ 'vertices' ]
	vertices = xmlElement.getRootElement().idDictionary[ verticesID ].object.getVertices()
	del xmlElement.attributeDictionary[ 'target' ]
	del xmlElement.attributeDictionary[ 'vertices' ]
	arrayDictionary = xmlElement.attributeDictionary.copy()
	targetMatrix4X4Copy = matrix4x4.Matrix4X4().getFromAttributeDictionary( target.attributeDictionary )
	matrix4x4.setAttributeDictionaryToMatrix( target.attributeDictionary, targetMatrix4X4Copy )
	xmlElement.className = 'group'
	for vertexIndex in xrange( len( vertices ) ):
		vertex = vertices[ vertexIndex ]
		vertexMatrix4X4 = matrix4x4.Matrix4X4( targetMatrix4X4Copy.matrixTetragrid )
		idHint = ''
		if 'id' in xmlElement.attributeDictionary:
			idHint = '%s_child_%s' % ( xmlElement.attributeDictionary[ 'id' ], vertexIndex )
		lastChild = target.getCopy( idHint, xmlElement )
		euclidean.overwriteDictionary( xmlElement.attributeDictionary, [ 'visible' ], lastChild.attributeDictionary )
		vertexAttributeDictionary = {}
		vertex.addToAttributeDictionary( vertexAttributeDictionary )
		matrix4x4.setXMLElementMatrixToMatrixAttributeDictionary( vertexAttributeDictionary, vertexMatrix4X4, lastChild )
	xmlElement.getRootElement().xmlProcessor.processXMLElement( xmlElement )
