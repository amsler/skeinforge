"""
Face of a triangle mesh.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.shapes.shape_tools.dictionary import Dictionary
from fabmetheus_utilities.shapes.shape_utilities import evaluate


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	evaluate.processArchivable( Comment, xmlElement, xmlProcessor )


class Comment( Dictionary ):
	"A comment."
	def addXML( self, depth, output ):
		"Add xml for this object."
		attributeDictionary = self.getAttributeDictionary()
		if len( attributeDictionary ) < 1:
			return
		output.write( attributeDictionary[ attributeDictionary.keys()[ 0 ] ] )

