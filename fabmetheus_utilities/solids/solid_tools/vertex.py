"""
Vertex of a triangle mesh.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement ):
	"Process the xml element."
	vertexDictionary = xmlElement.attributeDictionary
	vertex = Vector3( euclidean.getFloatZeroFromDictionary( 'x', vertexDictionary ), euclidean.getFloatZeroFromDictionary( 'y', vertexDictionary ), euclidean.getFloatZeroFromDictionary( 'z', vertexDictionary ) )
	xmlElement.parent.object.vertices.append( vertex )
