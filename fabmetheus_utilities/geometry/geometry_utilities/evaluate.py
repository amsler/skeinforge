"""
Boolean geometry utilities.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
import math
import os
import sys
import traceback


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


#Constants from: http://www.physlink.com/reference/MathConstants.cfm
#If anyone wants to add stuff, more constants are at: http://en.wikipedia.org/wiki/Mathematical_constant
globalMathConstantDictionary = {
	'e' : math.e,
	'euler' : 0.5772156649015328606065120,
	'golden' : 1.6180339887498948482045868,
	'pi' : math.pi }


def addPrefixDictionary( dictionary, keys, prefix, value ):
	"Add prefixed key values to dictionary."
	for key in keys:
		dictionary[ prefix + key ] = value

def addToPathsRecursively(paths, vector3Lists):
	"Add to vector3 paths recursively."
	if vector3Lists.__class__ == Vector3:
		paths.append([ vector3Lists ])
		return
	path = []
	for vector3List in vector3Lists:
		if vector3List.__class__ == list:
			addToPathsRecursively(paths, vector3List)
		elif vector3List.__class__ == Vector3:
			path.append(vector3List)
	if len(path) > 0:
		paths.append(path)

def compareExecutionOrderAscending( module, otherModule ):
	"Get comparison in order to sort modules in ascending execution order."
	if module.globalExecutionOrder < otherModule.globalExecutionOrder:
		return - 1
	return int( module.globalExecutionOrder > otherModule.globalExecutionOrder )

def convertToFloatLists(dictionary):
	'Recursively convert any Vector3 values to float lists.'
	for key in getKeys(dictionary):
		value = dictionary[key]
		if value.__class__ == Vector3:
			dictionary[key] = value.getFloatList()
		else:
			convertToFloatLists(dictionary[key])

def convertToPaths( dictionary ):
	'Recursively convert any XMLElements to paths.'
	for key in getKeys( dictionary ):
		value = dictionary[ key ]
		if value.__class__.__name__ == 'XMLElement':
			if value.object != None:
				dictionary[ key ] = getFloatListListsByPaths( value.object.getPaths() )
		else:
			convertToPaths( dictionary[ key ] )

def executeLeftOperations( evaluators, operationLevel ):
	"Evaluate the expression value from the numeric and operation evaluators."
	for negativeIndex in xrange( - len( evaluators ), - 1 ):
		evaluatorIndex = negativeIndex + len( evaluators )
		evaluators[ evaluatorIndex ].executeLeftOperation( evaluators, evaluatorIndex, operationLevel )

def executePairOperations( evaluators, operationLevel ):
	"Evaluate the expression value from the numeric and operation evaluators."
	for negativeIndex in xrange( 1 - len( evaluators ), - 1 ):
		evaluatorIndex = negativeIndex + len( evaluators )
		evaluators[ evaluatorIndex ].executePairOperation( evaluators, evaluatorIndex, operationLevel )

def getArchivableObject( archivableClass, xmlElement ):
	"Get the archivable object."
	archivableObject = archivableClass()
	archivableObject.xmlElement = xmlElement
	xmlElement.object = archivableObject
	archivableObject.setToObjectAttributeDictionary()
	xmlElement.parent.object.archivableObjects.append( archivableObject )
	return archivableObject

def getBooleanByNumber( number ):
	'Get boolean by number.'
	return float( number ) > 0.5

def getBracketEvaluators( bracketBeginIndex, bracketEndIndex, evaluators ):
	'Get the bracket evaluators.'
	return getEvaluatedExpressionValueEvaluators( evaluators[ bracketBeginIndex + 1 : bracketEndIndex ] )

def getBracketsExist( evaluators ):
	"Evaluate the expression value."
	bracketBeginIndex = None
	for negativeIndex in xrange( - len( evaluators ), 0 ):
		bracketEndIndex = negativeIndex + len( evaluators )
		evaluatorEnd = evaluators[ bracketEndIndex ]
		evaluatorWord = evaluatorEnd.word
		if evaluatorWord in ['(', '[', '{']:
			bracketBeginIndex = bracketEndIndex
		elif evaluatorWord in [')', ']', '}']:
			if bracketBeginIndex == None:
				print('Warning, bracketBeginIndex in evaluateBrackets in evaluate is None.')
				print('This may be because the brackets are not balanced.')
				print( evaluators )
				del evaluators[ bracketEndIndex ]
				return
			evaluators[ bracketBeginIndex ].executeBracket( bracketBeginIndex, bracketEndIndex, evaluators )
			evaluators[ bracketBeginIndex ].word = None
			return True
	return False

def getBracketValuesDeleteEvaluator( bracketBeginIndex, bracketEndIndex, evaluators ):
	'Get the bracket values and delete the evaluator.'
	evaluatedExpressionValueEvaluators = getBracketEvaluators( bracketBeginIndex, bracketEndIndex, evaluators )
	bracketValues = []
	for evaluatedExpressionValueEvaluator in evaluatedExpressionValueEvaluators:
		bracketValues.append( evaluatedExpressionValueEvaluator.value )
	del evaluators[ bracketBeginIndex + 1: bracketEndIndex + 1 ]
	return bracketValues

def getDictionarySplitWords( dictionary, value ):
	"Get split line for evaluators."
	if getIsQuoted( value ):
		return [ value ]
	for dictionaryKey in dictionary.keys():
		value = value.replace( dictionaryKey, ' ' + dictionaryKey + ' ')
	dictionarySplitWords = []
	for word in value.split():
		dictionarySplitWords.append( word )
	return dictionarySplitWords

def getElementByElement(xmlElement):
	"Get the xmlElement."
	return xmlElement

def getElementCascadeByElement(xmlElement):
	"Get the cascade xmlElement."
	return ElementCascade(xmlElement)

def getElementIDByElement(xmlElement):
	"Get the id xmlElement."
	return ElementID(xmlElement)

def getElementNameByElement(xmlElement):
	"Get the xmlElement."
	return ElementName(xmlElement)

def getEndIndexConvertEquationValue( bracketEndIndex, evaluatorIndex, evaluators ):
	'Get the bracket end index and convert the equation value evaluators into a string.'
	evaluator = evaluators[ evaluatorIndex ]
	if evaluator.__class__ != EvaluatorValue:
		return bracketEndIndex
	if not evaluator.word.startswith('equation.'):
		return bracketEndIndex
	if evaluators[ evaluatorIndex + 1 ].word != ':':
		return bracketEndIndex
	valueBeginIndex = evaluatorIndex + 2
	equationValueString = ''
	for valueEvaluatorIndex in xrange( valueBeginIndex, len( evaluators ) ):
		valueEvaluator = evaluators[ valueEvaluatorIndex ]
		if valueEvaluator.word == ',' or valueEvaluator.word == '}':
			if equationValueString == '':
				return bracketEndIndex
			else:
				evaluators[ valueBeginIndex ] = EvaluatorValue( equationValueString )
				valueDeleteIndex = valueBeginIndex + 1
				del evaluators[ valueDeleteIndex : valueEvaluatorIndex ]
			return bracketEndIndex - valueEvaluatorIndex + valueDeleteIndex
		equationValueString += valueEvaluator.word
	return bracketEndIndex

def getEvaluatedBooleanDefault( defaultBoolean, key, xmlElement ):
	"Get the evaluated boolean as a float."
	if key in xmlElement.attributeDictionary:
		return euclidean.getBooleanFromValue( getEvaluatedValueObliviously( key, xmlElement ) )
	return defaultBoolean

def getEvaluatedDictionary( evaluationKeys, xmlElement ):
	"Get the evaluated dictionary."
	evaluatedDictionary = {}
	zeroLength = ( len( evaluationKeys ) == 0 )
	for key in xmlElement.attributeDictionary.keys():
		if key in evaluationKeys or zeroLength:
			value = getEvaluatedValueObliviously( key, xmlElement )
			if value == '' or value == None:
				valueString = str( xmlElement.attributeDictionary[ key ]  )
				print('Warning, getEvaluatedDictionary in evaluate can not get a value for:')
				print( valueString )
				evaluatedDictionary[ key + '__Warning__'] = 'Can not evaluate: ' + valueString.replace('"', ' ').replace( "'", ' ')
			else:
				evaluatedDictionary[ key ] = value
	return evaluatedDictionary

def getEvaluatedExpressionValue( value, xmlElement ):
	"Evaluate the expression value."
	try:
		return getEvaluatedExpressionValueBySplitLine( getEvaluatorSplitWords( value ), xmlElement )
	except:
		print('Warning, in getEvaluatedExpressionValue in evaluate could not get a value for:')
		print( value )
		traceback.print_exc( file = sys.stdout )
		return None

def getEvaluatedExpressionValueBySplitLine( words, xmlElement ):
	"Evaluate the expression value."
	evaluators = []
	for wordIndex, word in enumerate( words ):
		nextWord = ''
		nextWordIndex = wordIndex + 1
		if nextWordIndex < len( words ):
			nextWord = words[ nextWordIndex ]
		evaluator = getEvaluator( evaluators, nextWord, word, xmlElement )
		if evaluator != None:
			evaluators.append( evaluator )
	while getBracketsExist( evaluators ):
		pass
	evaluatedExpressionValueEvaluators = getEvaluatedExpressionValueEvaluators( evaluators )
	if len( evaluatedExpressionValueEvaluators ) > 0:
		return evaluatedExpressionValueEvaluators[0].value
	return None

def getEvaluatedExpressionValueEvaluators( evaluators ):
	"Evaluate the expression value from the numeric and operation evaluators."
	for negativeIndex in xrange( 1 - len( evaluators ), 0 ):
		evaluatorIndex = negativeIndex + len( evaluators )
		evaluators[ evaluatorIndex ].executeRightOperation( evaluators, evaluatorIndex )
	executeLeftOperations( evaluators, 200 )
	for operationLevel in [ 80, 60, 40, 20, 15 ]:
		executePairOperations( evaluators, operationLevel )
	executeLeftOperations( evaluators, 13 )
	executePairOperations( evaluators, 12 )
	for negativeIndex in xrange( - len( evaluators ), 0 ):
		evaluatorIndex = negativeIndex + len( evaluators )
		evaluators[ evaluatorIndex ].executePairOperation( evaluators, evaluatorIndex, 10 )
	executePairOperations( evaluators, 0 )
	return evaluators

def getEvaluatedFloat( key, xmlElement ):
	"Get the evaluated value as a float."
	if key in xmlElement.attributeDictionary:
		return euclidean.getFloatFromValue( getEvaluatedValueObliviously( key, xmlElement ) )
	return None

def getEvaluatedFloatDefault( defaultFloat, key, xmlElement ):
	"Get the evaluated value as a float."
	evaluatedFloat = getEvaluatedFloat( key, xmlElement )
	if evaluatedFloat == None:
		return defaultFloat
	return evaluatedFloat

def getEvaluatedFloatOne( key, xmlElement ):
	"Get the evaluated value as a float with a default of one."
	return getEvaluatedFloatDefault( 1.0, key, xmlElement )

def getEvaluatedFloatZero( key, xmlElement ):
	"Get the evaluated value as a float with a default of zero."
	return getEvaluatedFloatDefault( 0.0, key, xmlElement )

def getEvaluatedInt( key, xmlElement ):
	"Get the evaluated value as an int."
	if key in xmlElement.attributeDictionary:
		try:
			return getIntFromFloatString( getEvaluatedValueObliviously( key, xmlElement ) )
		except:
			print('Warning, could not evaluate the int.')
			print(key)
			print( xmlElement.attributeDictionary[ key ] )
	return None

def getEvaluatedIntDefault( defaultInt, key, xmlElement ):
	"Get the evaluated value as an int."
	evaluatedInt = getEvaluatedInt( key, xmlElement )
	if evaluatedInt == None:
		return defaultInt
	return evaluatedInt

def getEvaluatedIntOne( key, xmlElement ):
	"Get the evaluated value as an int with a default of one."
	return getEvaluatedIntDefault( 1, key, xmlElement )

def getEvaluatedIntZero( key, xmlElement ):
	"Get the evaluated value as an int with a default of zero."
	return getEvaluatedIntDefault( 0, key, xmlElement )

def getEvaluatedLinkValue( word, xmlElement ):
	"Get the evaluated link value."
	if word == '':
		return None
	if getStartsWithCurlyEqualRoundSquare( word ) or getStartsWithChainWord( word ):
		return getEvaluatedExpressionValue( word, xmlElement )
	if gcodec.getStartsWithByList( word, ['creation.', 'math.'] ):
		return getEvaluatedExpressionValue( word, xmlElement )
	return word

def getEvaluatedLinkValueByLookingInDictionary( value, xmlElement ):
	"Evaluate the link value."
	if value in xmlElement.attributeDictionary:
		value = str( xmlElement.attributeDictionary[ value ] )
	return getEvaluatedLinkValue( value.lstrip(), xmlElement )

def getEvaluatedValue( key, xmlElement ):
	"Get the evaluated value."
	if key in xmlElement.attributeDictionary:
		return getEvaluatedValueObliviously( key, xmlElement )
	return None

def getEvaluatedValueObliviously( key, xmlElement ):
	"Get the evaluated value."
	value = str(xmlElement.attributeDictionary[key]).strip()
	if key == 'id' or key == 'name':
		return value
	return getEvaluatedLinkValue( value, xmlElement )

def getEvaluator( evaluators, nextWord, word, xmlElement ):
	"Get the evaluator."
	global globalSplitDictionary
	if word in globalSplitDictionary:
		return globalSplitDictionary[ word ]( word, xmlElement )
	if getStartsWithChainWord( word ):
		word = getValueByKeysXMLElement( word.split('.'), xmlElement )
		if word == None:
			return None
		if word.__class__.__name__ == 'XMLElement':
			if word.className == 'function':
				return EvaluatorFunction( str( word ), word )
			else:
				return EvaluatorValue( word )
		if word.__class__ != str:
			return EvaluatorValue( word )
	firstCharacter = word[ : 1 ]
	if firstCharacter == "'" or firstCharacter == '"':
		if len( word ) > 1:
			if firstCharacter == word[ - 1 ]:
				return EvaluatorValue( word[ 1 : - 1 ] )
	if firstCharacter.isalpha() or firstCharacter == '_':
		functions = xmlElement.getXMLProcessor().functions
		if len( functions ) > 0:
			if word in functions[ - 1 ].localDictionary:
				return EvaluatorLocal( word, xmlElement )
		functionElement = xmlElement.getXMLElementByImportID( word )
		if functionElement != None:
			if functionElement.className == 'function':
				return EvaluatorFunction( word, functionElement )
		return EvaluatorValue( word )
	return EvaluatorNumeric( word, xmlElement )

def getEvaluatorSplitWords( value ):
	"Get split words for evaluators."
	if value.startswith('='):
		value = value[ len('=') : ]
	if len( value ) < 1:
		return []
	global globalDictionaryOperatorBegin
	uniqueQuoteIndex = 0
	word = ''
	quoteString = None
	quoteDictionary = {}
	for characterIndex in xrange( len( value ) ):
		character = value[ characterIndex ]
		if character == '"' or character == "'":
			if quoteString == None:
				quoteString = ''
			elif quoteString != None:
				if character == quoteString[ : 1 ]:
					uniqueQuoteIndex = getUniqueQuoteIndex( uniqueQuoteIndex, value )
					uniqueToken = getTokenByNumber( uniqueQuoteIndex )
					quoteDictionary[ uniqueToken ] = quoteString + character
					character = uniqueToken
					quoteString = None
		if quoteString == None:
			word += character
		else:
			quoteString += character
	beginSplitWords = getDictionarySplitWords( globalDictionaryOperatorBegin, word )
	global globalSplitDictionaryOperator
	evaluatorSplitWords = []
	for beginSplitWord in beginSplitWords:
		if beginSplitWord in globalDictionaryOperatorBegin:
			evaluatorSplitWords.append( beginSplitWord )
		else:
			evaluatorSplitWords += getDictionarySplitWords( globalSplitDictionaryOperator, beginSplitWord )
	for evaluatorSplitWordIndex in xrange( len( evaluatorSplitWords ) ):
		evaluatorSplitWord = evaluatorSplitWords[ evaluatorSplitWordIndex ]
		for quoteDictionaryKey in quoteDictionary.keys():
			if quoteDictionaryKey in evaluatorSplitWord:
				evaluatorSplitWord = evaluatorSplitWord.replace( quoteDictionaryKey, quoteDictionary[ quoteDictionaryKey ] )
				evaluatorSplitWords[ evaluatorSplitWordIndex ] = evaluatorSplitWord
	return evaluatorSplitWords

def getFloatIfFloat( value ):
	'Get value as float if its string is a float.'
	if getTypeLength( value ) == - 1:
		return float( value )
	return value

def getFloatListFromBracketedString( bracketedString ):
	"Get list from a bracketed string."
	if not getIsBracketed( bracketedString ):
		return None
	bracketedString = bracketedString.strip().replace('[', '').replace(']', '').replace('(', '').replace(')', '')
	if len( bracketedString ) < 1:
		return []
	splitLine = bracketedString.split(',')
	floatList = []
	for word in splitLine:
		evaluatedFloat = euclidean.getFloatFromValue( word )
		if evaluatedFloat != None:
			floatList.append( evaluatedFloat )
	return floatList

def getFloatListListsByPaths( paths ):
	'Get float lists by paths.'
	floatListLists = []
	for path in paths:
		floatListList = []
		for point in path:
			floatListList.append( point.getFloatList() )
	return floatListLists

def getFromCreationEvaluatorPlugins( namePathDictionary, xmlElement ):
	"Get the creation evaluator plugins if the xmlElement is from the creation evaluator."
	if getEvaluatedBooleanDefault( False, '_fromCreationEvaluator', xmlElement ):
		return getMatchingPlugins( namePathDictionary, xmlElement )
	return []

def getGeometryDictionary(folderName):
	"Get to the geometry name path dictionary."
	geometryDictionary={}
	geometryDirectory = settings.getPathInFabmetheusUtilities('geometry')
	settings.addToNamePathDictionary(os.path.join(geometryDirectory, folderName), geometryDictionary)
	geometryPluginsDirectory = settings.getPathInFabmetheusUtilities('geometry_plugins')
	settings.addToNamePathDictionary(os.path.join(geometryPluginsDirectory, folderName), geometryDictionary)
	return geometryDictionary

def getGeometryDirectoryPath(subName=''):
	"Get the geometry directory path."
	path = settings.getPathInFabmetheusUtilities('geometry')
	if subName == '':
		return path
	return os.path.join(path, subName)

def getKeys( repository ):
	'Get keys for repository.'
	if repository.__class__ == list:
		return range( len( repository ) )
	if repository.__class__ == dict:
		return repository.keys()
	return []

def getIntFromFloatString( value ):
	"Get the int from the string."
	floatString = str( value ).strip()
	if floatString == '':
		return None
	dotIndex = floatString.find('.')
	if dotIndex < 0:
		return int( value )
	return int( round( float( floatString ) ) )

def getIsBracketed( word ):
	"Determine if the word is bracketed."
	if len( word ) < 2:
		return False
	firstCharacter = word[0]
	lastCharacter = word[ - 1 ]
	if firstCharacter == '(' and lastCharacter == ')':
		return True
	return firstCharacter == '[' and lastCharacter == ']'

def getIsQuoted( word ):
	"Determine if the word is quoted."
	if len( word ) < 2:
		return False
	firstCharacter = word[0]
	lastCharacter = word[ - 1 ]
	if firstCharacter == '"' and lastCharacter == '"':
		return True
	return firstCharacter == "'" and lastCharacter == "'"

def getMatchingPlugins( namePathDictionary, xmlElement ):
	"Get the plugins whose names are in the attribute dictionary."
	matchingPlugins = []
	namePathDictionaryCopy = namePathDictionary.copy()
	for key in xmlElement.attributeDictionary:
		dotIndex = key.find('.')
		if dotIndex > - 1:
			keyUntilDot = key[ : dotIndex ]
			if keyUntilDot in namePathDictionaryCopy:
				pluginModule = gcodec.getModuleWithPath( namePathDictionaryCopy[ keyUntilDot ] )
				del namePathDictionaryCopy[ keyUntilDot ]
				if pluginModule != None:
					matchingPlugins.append( pluginModule )
	return matchingPlugins

def getNextChildIndex(xmlElement):
	"Get the next child index."
	for childIndex, child in enumerate( xmlElement.parent.children ):
		if child == xmlElement:
			return childIndex + 1
	return len( xmlElement.parent.children )

def getParentByElement(xmlElement):
	"Get the parent."
	value = xmlElement.parent
	if value == None:
		print('Warning, could not get parent in getParentByElement in evaluate for:')
		print(xmlElement)
	return value

def getPathByKey( key, xmlElement ):
	"Get path from prefix and xml element."
	if key not in xmlElement.attributeDictionary:
		return []
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue( word, xmlElement )
	evaluatedLinkValueClass = evaluatedLinkValue.__class__
	if evaluatedLinkValueClass == list:
		return getPathByList( evaluatedLinkValue )
	if evaluatedLinkValueClass.__name__ != 'XMLElement':
		print('Warning, could not get XMLElement in getPathByKey in evaluate for:')
		print(key)
		print(evaluatedLinkValue)
		return []
	if evaluatedLinkValue.object == None:
		print('Warning, evaluatedLinkValue.object is None in getPathByKey in evaluate for:')
		print(key)
		print(evaluatedLinkValue)
		return []
	return evaluatedLinkValue.object.getPaths()[0]

def getPathByList( vertexList ):
	"Get the paths by list."
	if len( vertexList ) < 1:
		return Vector3()
	if vertexList[0].__class__ != list:
		vertexList = [ vertexList ]
	path = []
	for floatList in vertexList:
		vector3 = getVector3ByFloatList( floatList, Vector3() )
		path.append( vector3 )
	return path

def getPathByPrefix( path, prefix, xmlElement ):
	"Get path from prefix and xml element."
	if len( path ) < 2:
		print('Warning, bug, path is too small in evaluate in setPathByPrefix.')
		return
	pathByKey = getPathByKey( prefix + 'path', xmlElement )
	if len( pathByKey ) < len( path ):
		for pointIndex in xrange( len( pathByKey ) ):
			path[ pointIndex ] = pathByKey[ pointIndex ]
	else:
		path = pathByKey
	path[0] = getVector3ByPrefix( prefix + 'from', path[0], xmlElement )
	path[ - 1 ] = getVector3ByPrefix( prefix + 'to', path[ - 1 ], xmlElement )
	return path

def getPathsByKey( key, xmlElement ):
	"Get paths by key."
	if key not in xmlElement.attributeDictionary:
		return []
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue( word, xmlElement )
	evaluatedLinkValueClass = evaluatedLinkValue.__class__
	if evaluatedLinkValueClass == dict or evaluatedLinkValueClass == list:
		convertToPaths( evaluatedLinkValue )
		return getPathsByLists( evaluatedLinkValue )
	if evaluatedLinkValueClass.__name__ != 'XMLElement':
		print('Warning, could not get XMLElement in getPathsByKey in evaluate for the key:')
		print(key)
		print('Which gives the evaluatedLinkValue of:')
		print(evaluatedLinkValue)
		return []
	if evaluatedLinkValue.object == None:
		print('Warning, evaluatedLinkValue.object is None in getPathsByKey in evaluate for:')
		print(key)
		print(evaluatedLinkValue)
		return []
	return evaluatedLinkValue.object.getPaths()

def getPathsByKeys( keys, xmlElement ):
	"Get paths by keys."
	pathsByKeys = []
	for key in keys:
		pathsByKeys += getPathsByKey( key, xmlElement )
	return pathsByKeys

def getPathsByLists( vertexLists ):
	"Get paths by lists."
	vector3Lists = getVector3ListsRecursively( vertexLists )
	paths = []
	addToPathsRecursively( paths, vector3Lists )
	return paths

def getPrecision(xmlElement):
	"Get the cascade precision."
	if xmlElement == None:
		return 0.1
	return xmlElement.getCascadeFloat( 0.1, 'precision')

def getRootByElement(xmlElement):
	"Get the root."
	return xmlElement.getRoot()

def getSides(radius, xmlElement):
	"Get the nunber of poygon sides."
	return math.sqrt(0.5 * radius * math.pi * math.pi / getPrecision(xmlElement))

def getSidesMinimumThree(radius, xmlElement):
	"Get the nunber of poygon sides, with a minimum of three."
	return max(getSides(radius, xmlElement), 3.0)

def getSplitDictionary():
	"Get split dictionary."
	global globalSplitDictionaryOperator
	splitDictionary = globalSplitDictionaryOperator.copy()
	global globalDictionaryOperatorBegin
	splitDictionary.update( globalDictionaryOperatorBegin )
	addPrefixDictionary( splitDictionary, globalMathConstantDictionary.keys(), 'math.', EvaluatorConstant )
	splitDictionary['and'] = EvaluatorAnd
	splitDictionary['false'] = EvaluatorFalse
	splitDictionary['False'] = EvaluatorFalse
	splitDictionary['or'] = EvaluatorOr
	splitDictionary['not'] = EvaluatorNot
	splitDictionary['true'] = EvaluatorTrue
	splitDictionary['True'] = EvaluatorTrue
	global globalCreationDictionary
	for key in globalCreationDictionary.keys():
		splitDictionary['creation.get' + key.capitalize()] = EvaluatorCreation
	functionNameString = 'acos asin atan atan2 ceil cos cosh degrees exp fabs floor fmod frexp hypot ldexp log log10 modf pow radians sin sinh sqrt tan tanh'
	addPrefixDictionary( splitDictionary, functionNameString.split(), 'math.', EvaluatorMath )
	return splitDictionary

def getStartsWithChainWord( word ):
	"Determine if the word starts with an element chain word."
	if word.startswith('vertex'):
		return True
	dotIndex = word.find('.')
	if dotIndex < 0:
		return False
	return word[ : dotIndex ] in globalElementValueDictionary

def getStartsWithCurlyEqualRoundSquare( word ):
	"Determine if the word starts with round or square brackets."
	return word.startswith('{') or word.startswith('=') or word.startswith('(') or word.startswith('[')

def getTokenByNumber( number ):
	"Get token by number."
	return '_%s_' % number

def getTypeLength( value ):
	"Get the type length of the value."
	if value == None or value == '':
		return 0
	valueString = str( value )
	if valueString.startswith('{') or valueString.startswith('(') or valueString.startswith('['):
		return len( getKeys( value ) )
	if euclidean.getFloatFromValue( value ) == None:
		return 0
	return - 1

def getUniqueQuoteIndex( uniqueQuoteIndex, word ):
	"Get uniqueQuoteIndex."
	uniqueQuoteIndex += 1
	while getTokenByNumber( uniqueQuoteIndex ) in word:
		uniqueQuoteIndex += 1
	return uniqueQuoteIndex

def getValueByKeysXMLElement( keys, xmlElement ):
	"Get the value from the keys and xml element."
	for key in keys:
		if getIsQuoted( key ):
			key = key[ 1 : - 1 ]
		xmlElement = xmlElement.getValueByKey( key )
		if xmlElement == None:
			return None
	return xmlElement

def getVector3ByDictionary( dictionary, vector3 ):
	"Get vector3 by dictionary."
	if 'x' in dictionary:
		vector3.x = euclidean.getFloatFromValue( dictionary['x'] )
	if 'y' in dictionary:
		vector3.y = euclidean.getFloatFromValue( dictionary['y'] )
	if 'z' in dictionary:
		vector3.z = euclidean.getFloatFromValue( dictionary['z'] )
	return vector3

def getVector3ByDictionaryListValue( value, vector3 ):
	"Get vector3 by dictionary, list or value."
	if value.__class__ == dict:
		return getVector3ByDictionary( value, vector3 )
	if value.__class__ == list:
		return getVector3ByFloatList( value, vector3 )
	floatFromValue = euclidean.getFloatFromValue( value )
	if floatFromValue ==  None:
		return vector3
	vector3.setToXYZ( floatFromValue, floatFromValue, floatFromValue )
	return vector3

def getVector3ByFloatList(floatList, vector3):
	"Get vector3 by float list."
	if len(floatList) > 0:
		vector3.x = euclidean.getFloatFromValue(floatList[0])
	if len(floatList) > 1:
		vector3.y = euclidean.getFloatFromValue(floatList[1])
	if len(floatList) > 2:
		vector3.z = euclidean.getFloatFromValue(floatList[2])
	return vector3

def getVector3ByMultiplierPrefix( multiplier, prefix, vector3, xmlElement ):
	"Get vector3 from multiplier, prefix and xml element."
	if multiplier == 0.0:
		return vector3
	oldMultipliedValueVector3 = vector3 * multiplier
	vector3ByPrefix = getVector3ByPrefix( prefix, oldMultipliedValueVector3.copy(), xmlElement )
	if vector3ByPrefix == oldMultipliedValueVector3:
		return vector3
	return vector3ByPrefix / multiplier

def getVector3ByMultiplierPrefixes( multiplier, prefixes, vector3, xmlElement ):
	"Get vector3 from multiplier, prefixes and xml element."
	for prefix in prefixes:
		vector3 = getVector3ByMultiplierPrefix( multiplier, prefix, vector3, xmlElement )
	return vector3

def getVector3ByPrefix( prefix, vector3, xmlElement ):
	"Get vector3 from prefix and xml element."
	value = getEvaluatedValue( prefix, xmlElement )
	if value != None:
		vector3 = getVector3ByDictionaryListValue( value, vector3 )
	x = getEvaluatedFloat( prefix + '.x', xmlElement )
	if x != None:
		vector3 = getVector3IfNone( vector3 )
		vector3.x = x
	y = getEvaluatedFloat( prefix + '.y', xmlElement )
	if y != None:
		vector3 = getVector3IfNone( vector3 )
		vector3.y = y
	z = getEvaluatedFloat( prefix + '.z', xmlElement )
	if z != None:
		vector3 = getVector3IfNone( vector3 )
		vector3.z = z
	return vector3

def getVector3ByPrefixes( prefixes, vector3, xmlElement ):
	"Get vector3 from prefixes and xml element."
	for prefix in prefixes:
		vector3 = getVector3ByPrefix( prefix, vector3, xmlElement )
	return vector3

def getVector3FromXMLElement(xmlElement):
	"Get vector3 from xml element."
	return Vector3(getEvaluatedFloatZero('x', xmlElement), getEvaluatedFloatZero('y', xmlElement), getEvaluatedFloatZero('z', xmlElement))

def getVector3IfNone( vector3 ):
	"Get new vector3 if the original vector3 is none."
	if vector3 == None:
		return Vector3()
	return vector3

def getVector3ListsRecursively(floatLists):
	"Get vector3 lists recursively."
	if len(floatLists) < 1:
		return Vector3()
	firstElement = floatLists[0]
	if firstElement.__class__ == Vector3:
		return floatLists
	if firstElement.__class__ != list:
		return getVector3ByFloatList(floatLists, Vector3())
	vector3ListsRecursively = []
	for floatList in floatLists:
		vector3ListsRecursively.append(getVector3ListsRecursively(floatList))
	return vector3ListsRecursively

def getVector3RemoveByPrefix( prefix, vector3, xmlElement ):
	"Get vector3 from prefix and xml element, then remove prefix attributes from dictionary."
	vector3RemoveByPrefix = getVector3ByPrefix( prefix, vector3, xmlElement )
	euclidean.removePrefixFromDictionary( xmlElement.attributeDictionary, prefix )
	return vector3RemoveByPrefix

def getVertexByElement(xmlElement):
	"Get the vertex list."
	vertexElements = xmlElement.getChildrenWithClassName('vertex')
	path = []
	for vertexElement in vertexElements:
		path.append(getVector3FromXMLElement(vertexElement).getFloatList())
	return path

def getVerticesFromArchivableObjects( archivableObjects ):
	"Get all vertices."
	visibleObjects = getVisibleObjects( archivableObjects )
	vertices = []
	for visibleObject in visibleObjects:
		vertices += visibleObject.getVertices()
	return vertices

def getVisibleObjects( archivableObjects ):
	"Get the visible objects."
	visibleObjects = []
	for archivableObject in archivableObjects:
		if archivableObject.getVisible():
			visibleObjects.append( archivableObject )
	return visibleObjects

def getXMLElementByKey(key, xmlElement):
	"Get the xml element by key."
	if key not in xmlElement.attributeDictionary:
		return None
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue(word, xmlElement)
	if evaluatedLinkValue.__class__.__name__ != 'XMLElement':
		print('Warning, could not get XMLElement in getXMLElementByKey in evaluate for:')
		print(key)
		print(evaluatedLinkValue)
		print(xmlElement)
		return None
	return evaluatedLinkValue

def processArchivable( archivableClass, xmlElement, xmlProcessor ):
	"Get any new elements and process the archivable."
	if xmlElement == None:
		return
	getArchivableObject( archivableClass, xmlElement )
	xmlProcessor.processChildren(xmlElement)

def processCondition( xmlElement, xmlProcessor ):
	"Process the xml element condition."
	if xmlElement.object == None:
		xmlElement.object = ModuleXMLElement( xmlElement, xmlProcessor )
	if xmlElement.object.conditionSplitWords == None:
		return
	if len( xmlProcessor.functions ) < 1:
		print('Warning, "in" element is not in a function in processCondition in evaluate for:')
		print(xmlElement)
		return
	if int( getEvaluatedExpressionValueBySplitLine( xmlElement.object.conditionSplitWords, xmlElement ) ) > 0:
		xmlProcessor.functions[ - 1 ].processChildren(xmlElement)
	else:
		xmlElement.object.processElse( xmlElement, xmlProcessor )


class ElementCascade:
	"A class to get an element by cascade."
	def __init__( self, xmlElement ):
		"Initialize."
		self.xmlElement = xmlElement

	def getValueByKey( self, key ):
		"Get value by the key."
		value = self.xmlElement.getCascadeValue( None, key )
		if value == None:
			print('Warning, could not get value in ElementCascade in evaluate for:')
			print(key)
			print(xmlElement)
		return value


class ElementID:
	"A class to get an element by ID."
	def __init__( self, xmlElement ):
		"Initialize."
		self.xmlElement = xmlElement

	def getValueByKey( self, key ):
		"Get value by the key."
		value = self.xmlElement.getXMLElementByImportID( key )
		if value == None:
			print('Warning, could not get value in ElementID in evaluate for:')
			print(key)
			print( self.xmlElement )
		return value


class ElementName:
	"A class to get an element by name."
	def __init__( self, xmlElement ):
		"Initialize."
		self.xmlElement = xmlElement

	def getValueByKey( self, key ):
		"Get value by the key."
		value = self.xmlElement.getXMLElementByImportName( key )
		if value == None:
			print('Warning, could not get value in ElementName in evaluate for:')
			print(key)
			print( self.xmlElement )
		return value


class Evaluator:
	'Base evaluator class.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.value = None
		self.word = word

	def __repr__( self ):
		"Get the string representation of this Evaluator."
		return '%s: %s, %s' % ( self.__class__.__name__, self.word, self.value )

	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		pass

	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		pass

	def executeKey( self, evaluators, keys, evaluatorIndex, nextEvaluator ):
		'Execute the key index.'
		if self.value.__class__ == list:
			del evaluators[ evaluatorIndex ]
			if len( keys ) == 1:
				key = keys[0]
				if key.__class__ != KeyValue:
					nextEvaluator.value = self.getListValueByIntegerKey( key )
					if nextEvaluator.value == None:
						print('Warning, keyIndex in executeKey in Evaluator in evaluate is out of range for:')
						print( keyIndex )
						print( self.value )
					return
			nextEvaluator.value = []
			for key in keys:
				if key.__class__ == KeyValue:
					for keyIntegerIndex in key.getIntegerIndexes( len( self.value ) ):
						listValueByKeyIndex = self.getListValueByKeyIndex( keyIntegerIndex )
						if listValueByKeyIndex != None:
							nextEvaluator.value.append( listValueByKeyIndex )
				else:
					listValueByIntegerKey = self.getListValueByIntegerKey( key )
					if listValueByIntegerKey != None:
						nextEvaluator.value.append( listValueByIntegerKey )
			return
		if self.value.__class__ == dict:
			del evaluators[ evaluatorIndex ]
			if len( keys ) == 1:
				key = keys[0]
				if key.__class__ != KeyValue:
					if key in self.value:
						nextEvaluator.value = self.value[ key ]
					else:
						nextEvaluator.value = None
						print('Warning, key in executeKey in Evaluator in evaluate is not in for:')
						print(key)
						print( self.value )
					return
			nextEvaluator.value = []
			for key in keys:
				if key.__class__ == KeyValue:
					for keyIntegerIndex in key.getIntegerIndexes( len( self.value ) ):
						if keyIntegerIndex in self.value:
							nextEvaluator.value.append( self.value[ keyIntegerIndex ] )
				elif key in self.value:
					nextEvaluator.value.append( self.value[ key ] )

	def executeLeftOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Execute operator which acts from the left.'
		pass

	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		pass

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Execute operator which acts from the right.'
		pass

	def getListValueByIntegerKey( self, key ):
		'Execute the key index.'
		keyIndex = euclidean.getIntFromValue( key )
		if keyIndex == None:
			return None
		return self.getListValueByKeyIndex( keyIndex )

	def getListValueByKeyIndex( self, keyIndex ):
		'Get list value by keyIndex.'
		if keyIndex < 0 or keyIndex >= len( self.value ):
			return None
		return self.value[ keyIndex ]


class EvaluatorAddition( Evaluator ):
	'Class to add two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 20:
			self.executePair( evaluators, evaluatorIndex )

	def executePair( self, evaluators, evaluatorIndex ):
		'Add two evaluators.'
		leftIndex = evaluatorIndex - 1
		rightIndex = evaluatorIndex + 1
		if leftIndex < 0:
			del evaluators[ evaluatorIndex ]
			return
		if rightIndex >= len( evaluators ):
			del evaluators[ evaluatorIndex ]
			return
		leftValue = evaluators[ leftIndex ].value
		rightValue = evaluators[ rightIndex ].value
		operationValue = self.getOperationValue( leftValue, rightValue )
		evaluators[ leftIndex ].value = operationValue
		del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]

	def getOperationValue( self, leftValue, rightValue ):
		'Add two evaluators.'
		leftLength = getTypeLength( leftValue )
		rightLength = getTypeLength( rightValue )
		if leftLength == 0:
			return rightValue
		if rightLength == 0:
			return leftValue
		if leftLength == - 1 and rightLength == - 1:
			return self.getValueFromValuePair( leftValue, rightValue )
		leftKeys = getKeys( leftValue )
		rightKeys = getKeys( rightValue )
		allKeys = set( leftKeys ).union( set( rightKeys ) )
		dictionaryClass = dict
		evaluatedValues = []
		if leftValue.__class__ == dictionaryClass or rightValue.__class__ == dictionaryClass:
			evaluatedValues = {}
		for arrayIndex in allKeys:
			evaluatedValue = self.getValueFromIndexes( arrayIndex, leftKeys, leftValue, rightKeys, rightValue )
			if evaluatedValue != None:
				if evaluatedValues.__class__ == dictionaryClass:
					evaluatedValues[ arrayIndex ] = evaluatedValue
				else:
					evaluatedValues.append( evaluatedValue )
		return evaluatedValues

	def getValueFromIndex( self, arrayIndex, keys, value ):
		'Add two values.'
		if len( keys ) == 0:
			if getTypeLength( value ) == - 1:
				return float( value )
		if arrayIndex in keys:
			return getFloatIfFloat( value[ arrayIndex ] )
		return None

	def getValueFromIndexes( self, arrayIndex, leftKeys, leftValue, rightKeys, rightValue ):
		'Add two values.'
		leftValue = self.getValueFromIndex( arrayIndex, leftKeys, leftValue )
		rightValue = self.getValueFromIndex( arrayIndex, rightKeys, rightValue )
		if leftValue == None:
			return rightValue
		if rightValue == None:
			return leftValue
		return self.getOperationValue( leftValue, rightValue )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Add two values.'
		return leftValue + rightValue


class EvaluatorEqual( EvaluatorAddition ):
	'Class to compare two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 15:
			self.executePair( evaluators, evaluatorIndex )

	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'Compare two values.'
		return leftValue == rightValue

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Get value from comparison.'
		return int( self.getBooleanFromValuePair( leftValue, rightValue ) )


class EvaluatorSubtraction( EvaluatorAddition ):
	'Class to subtract two evaluators.'
	def executeLeft( self, evaluators, evaluatorIndex ):
		'Minus the value to the right.'
		leftIndex = evaluatorIndex - 1
		rightIndex = evaluatorIndex + 1
		leftValue = None
		if leftIndex >= 0:
			leftValue = evaluators[ leftIndex ].value
		if leftValue != None:
			return
		rightValue = evaluators[ rightIndex ].value
		if rightValue == None:
			print('Warning, can not minus.')
			print( evaluators[ rightIndex ].word )
		else:
			evaluators[ rightIndex ].value = self.getNegativeValue( rightValue )
		del evaluators[ evaluatorIndex ]

	def executeLeftOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Minus the value to the right.'
		if operationLevel == 200:
			self.executeLeft( evaluators, evaluatorIndex )

	def getNegativeValue( self, value ):
		'Get the negative value.'
		typeLength = getTypeLength( value )
		if typeLength < 0:
			return self.getValueFromSingleValue( value )
		if typeLength == 0:
			return None
		for key in getKeys( value ):
			value[ key ] = self.getNegativeValue( value[ key ] )
		return value

	def getValueFromSingleValue( self, value ):
		'Minus value.'
		return - float( value )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Subtract two values.'
		return leftValue - rightValue


class EvaluatorAnd( EvaluatorAddition ):
	'Class to compare two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 12:
			self.executePair( evaluators, evaluatorIndex )

	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'And two values.'
		return getBooleanByNumber( leftValue ) and getBooleanByNumber( rightValue )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Get value from comparison.'
		return int( self.getBooleanFromValuePair( leftValue, rightValue ) )


class EvaluatorBracketCurly( Evaluator ):
	'Class to evaluate a string.'
	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		for evaluatorIndex in xrange( bracketEndIndex - 3, bracketBeginIndex, - 1 ):
			bracketEndIndex = getEndIndexConvertEquationValue( bracketEndIndex, evaluatorIndex, evaluators )
		evaluatedExpressionValueEvaluators = getBracketEvaluators( bracketBeginIndex, bracketEndIndex, evaluators )
		self.value = {}
		for evaluatedExpressionValueEvaluator in evaluatedExpressionValueEvaluators:
			keyValue = evaluatedExpressionValueEvaluator.value
			self.value[ keyValue.keyTuple[0] ] = keyValue.keyTuple[1]
		del evaluators[ bracketBeginIndex + 1: bracketEndIndex + 1 ]


class EvaluatorBracketRound( Evaluator ):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.arguments = []
		self.value = None
		self.word = word

	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		self.arguments = getBracketValuesDeleteEvaluator( bracketBeginIndex, bracketEndIndex, evaluators )
		if len( self.arguments ) < 1:
			return
		if len( self.arguments ) > 1:
			self.value = self.arguments
		else:
			self.value = self.arguments[0]

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Evaluate the math statement and delete the evaluators.'
		previousIndex = evaluatorIndex - 1
		if previousIndex < 0:
			return
		evaluators[ previousIndex ].executeFunction( evaluators, previousIndex, self )


class EvaluatorBracketSquare( Evaluator ):
	'Class to evaluate a string.'
	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		self.value = getBracketValuesDeleteEvaluator( bracketBeginIndex, bracketEndIndex, evaluators )

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Evaluate the math statement and delete the evaluators.'
		previousIndex = evaluatorIndex - 1
		if previousIndex < 0:
			return
		if self.value.__class__ != list:
			return
		evaluators[ previousIndex ].executeKey( evaluators, self.value, previousIndex, self )


class EvaluatorComma( Evaluator ):
	'Class to join two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 0:
			del evaluators[ evaluatorIndex ]


class EvaluatorConcatenate( Evaluator ):
	'Class to join two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel != 80:
			return
		leftIndex = evaluatorIndex - 1
		if leftIndex < 0:
			del evaluators[ evaluatorIndex ]
			return
		rightIndex = evaluatorIndex + 1
		if rightIndex >= len( evaluators ):
			del evaluators[ leftIndex : rightIndex ]
			return
		leftValue = evaluators[ leftIndex ].value
		rightValue = evaluators[ rightIndex ].value
		if leftValue.__class__ == list and rightValue.__class__ == list:
			evaluators[ leftIndex ].value = leftValue + rightValue
			del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]
			return
		if leftValue.__class__ == list and rightValue.__class__ == int:
			if rightValue > 0:
				originalList = leftValue[ : ]
				for copyIndex in xrange( rightValue - 1 ):
					leftValue += originalList
				evaluators[ leftIndex ].value = leftValue
				del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]
			return
		if leftValue.__class__ == dict and rightValue.__class__ == dict:
			leftValue.update( rightValue )
			evaluators[ leftIndex ].value = leftValue
			del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]
			return
		del evaluators[ leftIndex : evaluatorIndex + 2 ]


class EvaluatorConstant( Evaluator ):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value.'
		self.word = word
		global globalMathConstantDictionary
		self.value = globalMathConstantDictionary[ word[ len('math.') : ] ]

def getVisibleObjects( archivableObjects ):
	"Get the visible objects."
	visibleObjects = []
	for archivableObject in archivableObjects:
		if archivableObject.getVisible():
			visibleObjects.append( archivableObject )
	return visibleObjects


class EvaluatorCreation(Evaluator):
	'Creation evaluator class.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.value = None
		self.word = word
		self.xmlElement = xmlElement

	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		functionName = self.word[len('creation.get') : ].lower()
		global globalCreationDictionary
		pluginModule = gcodec.getModuleWithPath(globalCreationDictionary[functionName])
		if pluginModule == None:
			print('Warning, the EvaluatorCreation in evaluate can not get a pluginModule for:')
			print(functionName)
			print(self)
			return
		dictionary = {'_fromCreationEvaluator': 'true'}
		firstArgument = None
		if len( nextEvaluator.arguments ) > 0:
			firstArgument = nextEvaluator.arguments[0]
		if firstArgument.__class__ == dict:
			dictionary.update(firstArgument)
			nextEvaluator.value = pluginModule.getGeometryOutput(self.xmlElement.getShallowCopy(dictionary))
		else:
			shallowCopy = self.xmlElement.getShallowCopy(dictionary)
			nextEvaluator.value = pluginModule.getGeometryOutputByArguments(nextEvaluator.arguments, shallowCopy)
		convertToFloatLists(nextEvaluator.value)
		del evaluators[evaluatorIndex]


class EvaluatorDictionary( Evaluator ):
	'Class to join two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel != 10:
			return
		leftValue = None
		leftEvaluatorIndex = evaluatorIndex - 1
		if leftEvaluatorIndex >= 0:
			leftValue = evaluators[ evaluatorIndex - 1 ].value
		rightIndex = evaluatorIndex + 1
		rightEvaluatorClass = EvaluatorComma
		if rightIndex < len( evaluators ):
			rightEvaluatorClass = evaluators[ rightIndex ].__class__
		if rightEvaluatorClass == EvaluatorComma or rightEvaluatorClass == EvaluatorDictionary:
			evaluators[ evaluatorIndex ].value = KeyValue( leftValue )
			if leftEvaluatorIndex >= 0:
				del evaluators[ leftEvaluatorIndex ]
			return
		keyValue = KeyValue( leftValue, evaluators[ rightIndex ].value )
		if leftEvaluatorIndex < 0:
			evaluators[ rightIndex ].value = keyValue
			del evaluators[ evaluatorIndex ]
			return
		evaluators[ rightIndex ].value = keyValue
		del evaluators[ leftEvaluatorIndex : rightIndex ]


class EvaluatorDivision( EvaluatorAddition ):
	'Class to divide two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 40:
			self.executePair( evaluators, evaluatorIndex )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Divide two values.'
		return leftValue / rightValue


class EvaluatorFalse( Evaluator ):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value to zero.'
		self.value = 0
		self.word = word


class EvaluatorFunction( EvaluatorCreation ):
	'Function evaluator class.'
	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		if self.xmlElement.object == None:
			if 'return' in self.xmlElement.attributeDictionary:
				value = self.xmlElement.attributeDictionary['return']
				self.xmlElement.object = getEvaluatorSplitWords( value )
			else:
				self.xmlElement.object = []
		self.function = Function( self.xmlElement.object, self.xmlElement )
		self.setFunctionLocalTable( nextEvaluator )
		nextEvaluator.value = self.function.getReturnValue()
		del evaluators[ evaluatorIndex ]

	def setFunctionLocalTable( self, nextEvaluator ):
		'Evaluate the function statement and delete the evaluators.'
		self.function.localDictionary['_arguments'] = nextEvaluator.arguments
		if len( nextEvaluator.arguments ) > 0:
			firstArgument = nextEvaluator.arguments[0]
			if firstArgument.__class__ == dict:
				self.function.localDictionary = firstArgument
				return
		if 'parameters' not in self.function.xmlElement.attributeDictionary:
			return
		parameters = self.function.xmlElement.attributeDictionary['parameters'].strip()
		if parameters == '':
			return
		parameterWords = parameters.split(',')
		for parameterWordIndex, parameterWord in enumerate( parameterWords ):
			strippedWord = parameterWord.strip()
			keyValue = KeyValue().getByEqual( strippedWord )
			if parameterWordIndex < len( nextEvaluator.arguments ):
				self.function.localDictionary[ keyValue.keyTuple[0] ] = nextEvaluator.arguments[ parameterWordIndex ]
			else:
				strippedValue = keyValue.keyTuple[1]
				if strippedValue == None:
					print('Warning there is no default parameter in getParameterValue for:')
					print( strippedWord )
					print( parameterWords )
					print( nextEvaluator.arguments )
					print( self.function.xmlElement.attributeDictionary )
				else:
					strippedValue = strippedValue.strip()
				self.function.localDictionary[ keyValue.keyTuple[0].strip() ] = strippedValue
		if len( nextEvaluator.arguments ) > len( parameterWords ):
			print('Warning there are too many function parameters for:')
			print( self.function.xmlElement.attributeDictionary )
			print( parameterWords )
			print( nextEvaluator.arguments )


class EvaluatorGreaterEqual( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'Compare two values.'
		return leftValue >= rightValue


class EvaluatorGreater( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'Compare two values.'
		return leftValue > rightValue


class EvaluatorLessEqual( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'Compare two values.'
		return leftValue <= rightValue


class EvaluatorLess( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'Compare two values.'
		return leftValue < rightValue


class EvaluatorLocal( EvaluatorCreation ):
	'Class to get a local variable.'
	def __init__(self, word, xmlElement):
		'Set value.'
		self.word = word
		self.value = None
		functions = xmlElement.getXMLProcessor().functions
		if len( functions ) < 1:
			return
		localDictionary = functions[ - 1 ].localDictionary
		if word in localDictionary:
			self.value = localDictionary[ word ]


class EvaluatorMath(EvaluatorCreation):
	'Math evaluator class.'
	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		function = math.__dict__[self.word[len('math.') : ].lower()]
		argumentsCopy = nextEvaluator.arguments[:]
		if len(argumentsCopy) == 1:
			firstElement = argumentsCopy[0]
			if firstElement.__class__ == list:
				argumentsCopy = firstElement
		while len(argumentsCopy) > 0:
			try:
				result = function(*argumentsCopy)
				nextEvaluator.value = result
				del evaluators[evaluatorIndex]
				return
			except:
				argumentsCopy = argumentsCopy[: -1]
		print('Warning, the EvaluatorMath in evaluate can not handle:')
		print(self)
		print(nextEvaluator.arguments)
		print(nextEvaluator)
		del evaluators[evaluatorIndex]


class EvaluatorModulo( EvaluatorDivision ):
	'Class to modulo two evaluators.'
	def getValueFromValuePair( self, leftValue, rightValue ):
		'Modulo two values.'
		return leftValue % rightValue

class EvaluatorMultiplication( EvaluatorDivision ):
	'Class to multiply two evaluators.'
	def getValueFromValuePair( self, leftValue, rightValue ):
		'Multiply two values.'
		return leftValue * rightValue


class EvaluatorNot( EvaluatorSubtraction ):
	'Class to compare two evaluators.'
	def executeLeftOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Minus the value to the right.'
		if operationLevel == 13:
			self.executeLeft( evaluators, evaluatorIndex )

	def getValueFromSingleValue( self, value ):
		'Minus value.'
		return int( not getBooleanByNumber( value ) )


class EvaluatorNotEqual( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'Compare two values.'
		return leftValue != rightValue


class EvaluatorNumeric( Evaluator ):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value.'
		self.value = None
		self.word = word
		try:
			if '.' in word:
				self.value = float( word )
			else:
				self.value = int( word )
		except:
			print('Warning, in EvaluatorNumeric in evaluate could not get a numeric value for:')
			print( word )


class EvaluatorOr( EvaluatorAnd ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair( self, leftValue, rightValue ):
		'Or two values.'
		return getBooleanByNumber( leftValue ) or getBooleanByNumber( rightValue )


class EvaluatorPower( EvaluatorAddition ):
	'Class to power two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 60:
			self.executePair( evaluators, evaluatorIndex )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Power of two values.'
		return leftValue ** rightValue


class EvaluatorTrue( Evaluator ):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value to one.'
		self.value = 1
		self.word = word


class EvaluatorValue( Evaluator ):
	'Class to evaluate a string.'
	def __init__( self, word ):
		'Set value to none.'
		self.value = word
		self.word = str( word )


class Function:
	"Class to get equation results."
	def __init__( self, evaluatorSplitLine, xmlElement ):
		"Initialize."
		self.evaluatorSplitLine = evaluatorSplitLine
		self.localDictionary = {}
		self.returnValue = None
		self.xmlElement = xmlElement
		self.xmlProcessor = xmlElement.getXMLProcessor()
		self.xmlProcessor.functions.append( self )

	def __repr__( self ):
		"Get the string representation of this Function."
		return '%s, %s, %s' % ( self.evaluatorSplitLine, self.localDictionary, self.returnValue )

	def getReturnValue( self ):
		"Get return value."
		self.getReturnValueWithoutDeletion()
		self.reset()
		return self.returnValue

	def getReturnValueWithoutDeletion( self ):
		"Get return value without deleting last function."
		if len( self.evaluatorSplitLine ) < 1:
			self.shouldReturn = False
			self.processChildren( self.xmlElement )
		else:
			self.returnValue = getEvaluatedExpressionValueBySplitLine( self.evaluatorSplitLine, self.xmlElement )
		return self.returnValue

	def processChildren( self, xmlElement ):
		"Process children if shouldReturn is false."
		for child in xmlElement.children:
			if self.shouldReturn:
				return
			self.xmlProcessor.processXMLElement( child )

	def reset( self ):
		"Reset functions."
		del self.xmlElement.getXMLProcessor().functions[ - 1 ]


class KeyValue:
	"Class to hold a key value."
	def __init__( self, key = None, value = None ):
		"Get key value."
		if key.__class__ == KeyValue:
			self.keyTuple = key.keyTuple + ( value, )
			return
		self.keyTuple = ( key, value )

	def __repr__( self ):
		"Get the string representation of this KeyValue."
		return str( self.keyTuple )

	def getByCharacter( self, character, line ):
		"Get by character."
		dotIndex = line.find( character )
		if dotIndex < 0:
			self.keyTuple = ( line, None )
			return self
		self.keyTuple = ( line[ : dotIndex ], line[ dotIndex + 1 : ] )
		return self

	def getByDot( self, line ):
		"Get by dot."
		return self.getByCharacter('.', line )

	def getByEqual( self, line ):
		"Get by dot."
		return self.getByCharacter('=', line )

	def getIntegerIndexes( self, endIndexDefault ):
		"Get integer indexes."
		beginIndex = None
		beginIndexDefault = 0
		endIndex = None
		if self.keyTuple[0] != None:
			beginIndex = euclidean.getIntFromValue( self.keyTuple[0] )
			if beginIndex == None:
				print('Warning, beginIndex in getIntegerIndexes in evaluate is None for:')
				print( self.keyTuple )
				return None
		if self.keyTuple[1] != None:
			endIndex = euclidean.getIntFromValue( self.keyTuple[1] )
			if endIndex == None:
				print('Warning, beginIndex in getIntegerIndexes in evaluate is None for:')
				print( self.keyTuple )
				return None
		if len( self.keyTuple ) < 3:
			if beginIndex == None:
				beginIndex = beginIndexDefault
			if endIndex == None:
				endIndex = endIndexDefault
			return range( beginIndex, endIndex )
		step = 1
		if self.keyTuple[2] != None:
			step = euclidean.getIntFromValue( self.keyTuple[2] )
			if step == None:
				print('Warning, step in getIntegerIndexes in evaluate is None for:')
				print( self.keyTuple )
				return None
		if step == 0:
			print('Warning, step in getIntegerIndexes in evaluate is 0 for:')
			print( self.keyTuple )
			return None
		if step < 0:
			beginIndexDefault = endIndexDefault
			endIndexDefault = 0
		if beginIndex == None:
			beginIndex = beginIndexDefault
		if endIndex == None:
			endIndex = endIndexDefault
		return range( beginIndex, endIndex, step )


class ModuleXMLElement:
	"Class to get the in attribute, the index name and the value name."
	def __init__( self, xmlElement, xmlProcessor ):
		"Initialize."
		self.conditionSplitWords = None
		self.elseElement = None
		if 'condition' in xmlElement.attributeDictionary:
			self.conditionSplitWords = getEvaluatorSplitWords( xmlElement.attributeDictionary['condition'] )
		else:
			print('Warning, could not find the "condition" attribute in ModuleXMLElement in evaluate for:')
			print(xmlElement)
			return
		if len( self.conditionSplitWords ) < 1:
			self.conditionSplitWords = None
			print('Warning, could not get split words for the "condition" attribute in ModuleXMLElement in evaluate for:')
			print(xmlElement)
		nextIndex = getNextChildIndex(xmlElement)
		if nextIndex >= len( xmlElement.parent.children ):
			return
		nextXMLElement = xmlElement.parent.children[ nextIndex ]
		lowerClassName = nextXMLElement.className.lower()
		if lowerClassName != 'else' and lowerClassName != 'elif':
			return
		if lowerClassName not in xmlProcessor.namePathDictionary:
			return
		self.pluginModule = gcodec.getModuleWithPath( xmlProcessor.namePathDictionary[ lowerClassName ] )
		if self.pluginModule == None:
			return
		self.elseElement = nextXMLElement

	def processElse( self, xmlElement, xmlProcessor ):
		"Process the else statement."
		if self.elseElement != None:
			self.pluginModule.processElse( self.elseElement, xmlProcessor )


globalCreationDictionary = getGeometryDictionary('creation')
globalDictionaryOperatorBegin = {
	'||' : EvaluatorConcatenate,
	'==' : EvaluatorEqual,
	'>=' : EvaluatorGreaterEqual,
	'<=' : EvaluatorLessEqual,
	'!=' : EvaluatorNotEqual,
	'**' : EvaluatorPower }
globalElementValueDictionary = {
	'cascade' : getElementCascadeByElement,
	'element' : getElementByElement,
	'id' : getElementIDByElement,
	'name' : getElementNameByElement,
	'parent' : getParentByElement,
	'root' : getRootByElement,
	'vertex' : getVertexByElement }
globalSplitDictionaryOperator = {
	'+' : EvaluatorAddition,
	'{' : EvaluatorBracketCurly,
	'}' : Evaluator,
	'(' : EvaluatorBracketRound,
	')' : Evaluator,
	'[' : EvaluatorBracketSquare,
	']' : Evaluator,
	',' : EvaluatorComma,
	':' : EvaluatorDictionary,
	'/' : EvaluatorDivision,
	'>' : EvaluatorGreater,
	'<' : EvaluatorLess,
	'%' : EvaluatorModulo,
	'*' : EvaluatorMultiplication,
	'-' : EvaluatorSubtraction }
globalSplitDictionary = getSplitDictionary() # must be after globalSplitDictionaryOperator
