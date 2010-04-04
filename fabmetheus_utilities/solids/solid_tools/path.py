"""
Face of a triangle mesh.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools.dictionary import Dictionary
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.solids.solid_tools import matrix4x4
from fabmetheus_utilities import xml_simple_writer


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement ):
	"Process the xml element."
	geomancer.processArchivable( Path, xmlElement )


class Path( Dictionary ):
	"A path."
	def __init__( self ):
		"Add empty lists."
		Dictionary.__init__( self )
		self.vertices = []

	def addXMLInnerSection( self, depth, output ):
		"Add the xml section for this object."
		xml_simple_writer.addXMLFromObjects( depth, self.vertices, output )

