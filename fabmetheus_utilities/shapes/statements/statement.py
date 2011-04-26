"""
Polygon path.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.shapes.shape_utilities import evaluate


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getLocalAttribute( xmlElement ):
	"Get the local attribute if any."
	for key in xmlElement.attributeDictionary:
		if key[ : 1 ].isalpha():
			value = evaluate.getEvaluatorSplitWords( xmlElement.attributeDictionary[ key ] )
			if key.startswith( 'local.' ):
				return evaluate.KeyValue( key[ len( 'local.' ) : ], value )
			return evaluate.KeyValue( key, value )
	return evaluate.KeyValue()

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	functions = xmlProcessor.functions
	if len( functions ) < 1:
		return
	function = functions[ - 1 ]
	if xmlElement.object == None:
		xmlElement.object = getLocalAttribute( xmlElement )
	if xmlElement.object.keyTuple[ 1 ] != None:
		localValue = evaluate.getEvaluatedExpressionValueBySplitLine( xmlElement.object.keyTuple[ 1 ], xmlElement )
		function.localTable[ xmlElement.object.keyTuple[ 0 ] ] = localValue
