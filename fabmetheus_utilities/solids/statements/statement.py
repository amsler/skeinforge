"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_utilities import geomancer


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getLocalAttribute( xmlElement ):
	"Get the local attribute if any."
	for key in xmlElement.attributeDictionary:
		if key.startswith( 'local.' ):
			value = xmlElement.attributeDictionary[ key ]
			return geomancer.KeyValue( key[ len( 'local.' ) : ], geomancer.getEvaluatorSplitLine( value, xmlElement ) )
	return geomancer.KeyValue()

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	functions = xmlProcessor.functions
	if len( functions ) < 1:
		return
	function = functions[ - 1 ]
	if xmlElement.object == None:
		xmlElement.object = getLocalAttribute( xmlElement )
	if xmlElement.object.value != None:
		localValue = geomancer.getEvaluatedExpressionValueBySplitLine( xmlElement.object.value, xmlElement )
		function.localTable[ xmlElement.object.key ] = localValue
