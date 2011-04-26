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


def getLocalDictionary( attributeDictionaryKey, xmlElement, xmlProcessor ):
	"Get the local dictionary."
	if len( xmlProcessor.functions ) < 1:
		return None
	return xmlProcessor.functions[ - 1 ].localDictionary

def printAttributeDictionaryKey( attributeDictionaryKey, xmlElement, xmlProcessor ):
	"Print the attributeDictionaryKey."
	if attributeDictionaryKey.lower() == '_localdictionary':
		localDictionary = getLocalDictionary( attributeDictionaryKey, xmlElement, xmlProcessor )
		if localDictionary != None:
			localDictionaryKeys = localDictionary.keys()
			attributeValue = xmlElement.attributeDictionary[ attributeDictionaryKey ]
			if attributeValue != '':
				attributeValue = ' - ' + attributeValue
			print( 'Local Dictionary Variables' + attributeValue )
			localDictionaryKeys.sort()
			for localDictionaryKey in localDictionaryKeys:
				print( '%s: %s' % ( localDictionaryKey, localDictionary[ localDictionaryKey ] ) )
			return
	value = xmlElement.attributeDictionary[ attributeDictionaryKey ]
	evaluatedValue = None
	if value == '':
		evaluatedValue = evaluate.getEvaluatedExpressionValue( attributeDictionaryKey, xmlElement )
	else:
		evaluatedValue = evaluate.getEvaluatedExpressionValue( value, xmlElement )
	print( '%s: %s' % ( attributeDictionaryKey, evaluatedValue ) )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	attributeDictionaryKeys = xmlElement.attributeDictionary.keys()
	if len( attributeDictionaryKeys ) < 1:
		print( '' )
		return
	attributeDictionaryKeys.sort()
	for attributeDictionaryKey in attributeDictionaryKeys:
		printAttributeDictionaryKey( attributeDictionaryKey, xmlElement, xmlProcessor )
