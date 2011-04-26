"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_utilities import evaluate


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def processElse( xmlElement, xmlProcessor ):
	"Process the else statement."
	functions = xmlProcessor.functions
	if len( functions ) < 1:
		print( 'Warning, "else" element is not in a function in processElse in else.py for:' )
		print( xmlElement )
		return
	functions[ - 1 ].processChildren( xmlElement )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	pass
