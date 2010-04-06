"""
Boolean geometry translation.

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
	targetID = xmlElement.attributeDictionary[ 'target' ]
	target = xmlElement.getRootElement().idDictionary[ targetID ]
	del xmlElement.attributeDictionary[ 'target' ]
	translateDictionary = xmlElement.attributeDictionary.copy()
	targetMatrix4X4Copy = matrix4x4.Matrix4X4().getFromAttributeDictionary( target.attributeDictionary )
	xmlElement.attributeDictionary = target.attributeDictionary.copy()
	matrix4x4.setAttributeDictionaryToMatrix( target.attributeDictionary, targetMatrix4X4Copy )
	euclidean.overwriteDictionary( translateDictionary, [ 'visible' ], xmlElement.attributeDictionary )
	xmlElement.className = target.className
	matrix4x4.setXMLElementMatrixToMatrixAttributeDictionary( xmlElement.attributeDictionary, targetMatrix4X4Copy, xmlElement )
	target.copyXMLChildren( xmlElement )
	xmlElement.getRootElement().xmlProcessor.processXMLElement( xmlElement )
