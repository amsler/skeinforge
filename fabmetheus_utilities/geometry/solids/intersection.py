"""
Boolean geometry intersection of solids.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.solids import difference
from fabmetheus_utilities.geometry.solids import group


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def convertXMLElement( geometryOutput, xmlElement, xmlProcessor ):
	"Convert the xml element to an intersection xml element."
	xmlProcessor.createChildren( geometryOutput, xmlElement )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	group.processShape( Intersection, xmlElement, xmlProcessor )


class Intersection( difference.Difference ):
	"An intersection object."
	def getLoopsFromObjectLoopsList( self, importRadius, visibleObjectLoopsList ):
		"Get loops from visible object loops list."
		return self.getIntersection( importRadius, visibleObjectLoopsList )
