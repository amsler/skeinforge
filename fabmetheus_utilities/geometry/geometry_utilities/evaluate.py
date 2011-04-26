"""
Boolean geometry utilities.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import archive
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
import math
import os
import sys
import traceback


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = 'GPL 3.0'


globalModuleFunctionsDictionary = {}


def addAttributeWord(evaluatorWords, word):
	"Add attribute word and remainder if the word starts with a dot, otherwise add the word."
	if len(word) < 2:
		evaluatorWords.append(word)
		return
	if word[0] != '.':
		evaluatorWords.append(word)
		return
	dotIndex = word.find('.', 1)
	if dotIndex < 0:
		evaluatorWords.append(word)
		return
	evaluatorWords.append(word[: dotIndex])
	addAttributeWord(evaluatorWords, word[dotIndex :])

def addQuoteWord(evaluatorWords, word):
	"Add quote word and remainder if the word starts with a quote character or dollar sign, otherwise add the word."
	if len(word) < 2:
		evaluatorWords.append(word)
		return
	firstCharacter = word[0]
	if firstCharacter == '$':
		dotIndex = word.find('.', 1)
		if dotIndex > -1:
			evaluatorWords.append(word[: dotIndex])
			evaluatorWords.append(word[dotIndex :])
			return
	if firstCharacter != '"' and firstCharacter != "'":
		evaluatorWords.append(word)
		return
	nextQuoteIndex = word.find(firstCharacter, 1)
	if nextQuoteIndex < 0 or nextQuoteIndex == len(word) - 1:
		evaluatorWords.append(word)
		return
	nextQuoteIndex += 1
	evaluatorWords.append(word[: nextQuoteIndex])
	evaluatorWords.append(word[nextQuoteIndex :])

def addPrefixDictionary(dictionary, keys, value):
	"Add prefixed key values to dictionary."
	for key in keys:
		dictionary[key.lstrip('_')] = value

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

def addVector3ToXMLElement(key, vector3, xmlElement):
	"Add vector3 to xml element."
	xmlElement.attributeDictionary[key] = '[%s,%s,%s]' % (vector3.x, vector3.y, vector3.z)

def compareExecutionOrderAscending(module, otherModule):
	"Get comparison in order to sort modules in ascending execution order."
	if module.globalExecutionOrder < otherModule.globalExecutionOrder:
		return -1
	if module.globalExecutionOrder > otherModule.globalExecutionOrder:
		return 1
	if module.__name__ < otherModule.__name__:
		return -1
	return int(module.__name__ > otherModule.__name__)

def convertToPaths(dictionary):
	'Recursively convert any XMLElements to paths.'
	if dictionary.__class__ == Vector3 or dictionary.__class__.__name__ == 'Vector3Index':
		return
	keys = getKeys(dictionary)
	if keys == None:
		return
	for key in keys:
		value = dictionary[key]
		if value.__class__.__name__ == 'XMLElement':
			if value.object != None:
				dictionary[key] = getFloatListListsByPaths(value.object.getPaths())
		else:
			convertToPaths(dictionary[key])

def convertToTransformedPaths(dictionary):
	'Recursively convert any XMLElements to paths.'
	if dictionary.__class__ == Vector3 or dictionary.__class__.__name__ == 'Vector3Index':
		return
	keys = getKeys(dictionary)
	if keys == None:
		return
	for key in keys:
		value = dictionary[key]
		if value.__class__.__name__ == 'XMLElement':
			if value.object != None:
				dictionary[key] = value.object.getTransformedPaths()
		else:
			convertToTransformedPaths(dictionary[key])

def executeLeftOperations( evaluators, operationLevel ):
	"Evaluate the expression value from the numeric and operation evaluators."
	for negativeIndex in xrange( - len(evaluators), - 1 ):
		evaluatorIndex = negativeIndex + len(evaluators)
		evaluators[evaluatorIndex].executeLeftOperation( evaluators, evaluatorIndex, operationLevel )

def executePairOperations(evaluators, operationLevel):
	"Evaluate the expression value from the numeric and operation evaluators."
	for negativeIndex in xrange(1 - len(evaluators), - 1):
		evaluatorIndex = negativeIndex + len(evaluators)
		evaluators[evaluatorIndex].executePairOperation(evaluators, evaluatorIndex, operationLevel)

def getArchivableObjectAddToParent( archivableClass, xmlElement ):
	"Get the archivable object and add it to the parent object."
	archivableObject = archivableClass()
	archivableObject.xmlElement = xmlElement
	xmlElement.object = archivableObject
	archivableObject.setToObjectAttributeDictionary()
	xmlElement.parent.object.archivableObjects.append(archivableObject)
	return archivableObject

def getBracketEvaluators(bracketBeginIndex, bracketEndIndex, evaluators):
	'Get the bracket evaluators.'
	return getEvaluatedExpressionValueEvaluators(evaluators[bracketBeginIndex + 1 : bracketEndIndex])

def getBracketsExist(evaluators):
	"Evaluate the expression value."
	bracketBeginIndex = None
	for negativeIndex in xrange( - len(evaluators), 0 ):
		bracketEndIndex = negativeIndex + len(evaluators)
		evaluatorEnd = evaluators[ bracketEndIndex ]
		evaluatorWord = evaluatorEnd.word
		if evaluatorWord in ['(', '[', '{']:
			bracketBeginIndex = bracketEndIndex
		elif evaluatorWord in [')', ']', '}']:
			if bracketBeginIndex == None:
				print('Warning, bracketBeginIndex in evaluateBrackets in evaluate is None.')
				print('This may be because the brackets are not balanced.')
				print(evaluators)
				del evaluators[ bracketEndIndex ]
				return
			evaluators[ bracketBeginIndex ].executeBracket(bracketBeginIndex, bracketEndIndex, evaluators)
			evaluators[ bracketBeginIndex ].word = None
			return True
	return False

def getBracketValuesDeleteEvaluator(bracketBeginIndex, bracketEndIndex, evaluators):
	'Get the bracket values and delete the evaluator.'
	evaluatedExpressionValueEvaluators = getBracketEvaluators(bracketBeginIndex, bracketEndIndex, evaluators)
	bracketValues = []
	for evaluatedExpressionValueEvaluator in evaluatedExpressionValueEvaluators:
		bracketValues.append( evaluatedExpressionValueEvaluator.value )
	del evaluators[ bracketBeginIndex + 1: bracketEndIndex + 1 ]
	return bracketValues

def getCumulativeVector3(prefix, vector3, xmlElement):
	"Get cumulative vector3 and delete the prefixed attributes."
	cumulativeVector3 = getVector3ByPrefix(prefix + 'rectangular', vector3, xmlElement)
	cylindrical = getVector3ByPrefix(prefix + 'cylindrical', Vector3(), xmlElement)
	if not cylindrical.getIsDefault():
		cylindricalComplex = euclidean.getWiddershinsUnitPolar(math.radians(cylindrical.y)) * cylindrical.x
		cumulativeVector3 += Vector3(cylindricalComplex.real, cylindricalComplex.imag, cylindrical.z)
	polar = getVector3ByPrefix(prefix + 'polar', Vector3(), xmlElement)
	if not polar.getIsDefault():
		polarComplex = euclidean.getWiddershinsUnitPolar(math.radians(polar.y)) * polar.x
		cumulativeVector3 += Vector3(polarComplex.real, polarComplex.imag)
	spherical = getVector3ByPrefix(prefix + 'spherical', Vector3(), xmlElement)
	if not spherical.getIsDefault():
		radius = spherical.x
		elevationComplex = euclidean.getWiddershinsUnitPolar(math.radians(spherical.z)) * radius
		azimuthComplex = euclidean.getWiddershinsUnitPolar(math.radians(spherical.y)) * elevationComplex.real
		cumulativeVector3 += Vector3(azimuthComplex.real, azimuthComplex.imag, elevationComplex.imag)
	return cumulativeVector3

def getDictionarySplitWords(dictionary, value):
	"Get split line for evaluators."
	if getIsQuoted(value):
		return [value]
	for dictionaryKey in dictionary.keys():
		value = value.replace(dictionaryKey, ' ' + dictionaryKey + ' ')
	dictionarySplitWords = []
	for word in value.split():
		dictionarySplitWords.append(word)
	return dictionarySplitWords

def getEndIndexConvertEquationValue( bracketEndIndex, evaluatorIndex, evaluators ):
	'Get the bracket end index and convert the equation value evaluators into a string.'
	evaluator = evaluators[evaluatorIndex]
	if evaluator.__class__ != EvaluatorValue:
		return bracketEndIndex
	if not evaluator.word.startswith('equation.'):
		return bracketEndIndex
	if evaluators[ evaluatorIndex + 1 ].word != ':':
		return bracketEndIndex
	valueBeginIndex = evaluatorIndex + 2
	equationValueString = ''
	for valueEvaluatorIndex in xrange( valueBeginIndex, len(evaluators) ):
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

def getEvaluatedBooleanDefault(defaultBoolean, key, xmlElement=None):
	"Get the evaluated boolean as a float."
	if xmlElement == None:
		return None
	if key in xmlElement.attributeDictionary:
		return euclidean.getBooleanFromValue(getEvaluatedValueObliviously(key, xmlElement))
	return defaultBoolean

def getEvaluatedDictionary( evaluationKeys, xmlElement ):
	"Get the evaluated dictionary."
	evaluatedDictionary = {}
	zeroLength = (len(evaluationKeys) == 0)
	for key in xmlElement.attributeDictionary.keys():
		if key in evaluationKeys or zeroLength:
			value = getEvaluatedValueObliviously(key, xmlElement)
			if value == None:
				valueString = str( xmlElement.attributeDictionary[key]  )
				print('Warning, getEvaluatedDictionary in evaluate can not get a value for:')
				print( valueString )
				evaluatedDictionary[key + '__Warning__'] = 'Can not evaluate: ' + valueString.replace('"', ' ').replace( "'", ' ')
			else:
				evaluatedDictionary[key] = value
	return evaluatedDictionary

def getEvaluatedExpressionValue(value, xmlElement):
	"Evaluate the expression value."
	try:
		return getEvaluatedExpressionValueBySplitLine( getEvaluatorSplitWords(value), xmlElement )
	except:
		print('Warning, in getEvaluatedExpressionValue in evaluate could not get a value for:')
		print(value)
		traceback.print_exc(file=sys.stdout)
		return None

def getEvaluatedExpressionValueBySplitLine(words, xmlElement):
	"Evaluate the expression value."
	evaluators = []
	for wordIndex, word in enumerate(words):
		nextWord = ''
		nextWordIndex = wordIndex + 1
		if nextWordIndex < len(words):
			nextWord = words[nextWordIndex]
		evaluator = getEvaluator(evaluators, nextWord, word, xmlElement)
		if evaluator != None:
			evaluators.append(evaluator)
	while getBracketsExist(evaluators):
		pass
	evaluatedExpressionValueEvaluators = getEvaluatedExpressionValueEvaluators(evaluators)
	if len( evaluatedExpressionValueEvaluators ) > 0:
		return evaluatedExpressionValueEvaluators[0].value
	return None

def getEvaluatedExpressionValueEvaluators(evaluators):
	"Evaluate the expression value from the numeric and operation evaluators."
	for evaluatorIndex, evaluator in enumerate(evaluators):
		evaluator.executeCenterOperation(evaluators, evaluatorIndex)
	for negativeIndex in xrange( 1 - len(evaluators), 0 ):
		evaluatorIndex = negativeIndex + len(evaluators)
		evaluators[evaluatorIndex].executeRightOperation(evaluators, evaluatorIndex)
	executeLeftOperations( evaluators, 200 )
	for operationLevel in [ 80, 60, 40, 20, 15 ]:
		executePairOperations( evaluators, operationLevel )
	executeLeftOperations( evaluators, 13 )
	executePairOperations( evaluators, 12 )
	for negativeIndex in xrange( - len(evaluators), 0 ):
		evaluatorIndex = negativeIndex + len(evaluators)
		evaluators[evaluatorIndex].executePairOperation( evaluators, evaluatorIndex, 10 )
	for evaluatorIndex in xrange(len(evaluators) - 1, -1, -1):
		evaluators[evaluatorIndex].executePairOperation(evaluators, evaluatorIndex, 0)
	return evaluators

def getEvaluatedFloat(key, xmlElement=None):
	"Get the evaluated value as a float."
	if xmlElement == None:
		return None
	if key in xmlElement.attributeDictionary:
		return euclidean.getFloatFromValue(getEvaluatedValueObliviously(key, xmlElement))
	return None

def getEvaluatedFloatByKeys(defaultFloat, keys, xmlElement):
	"Get the evaluated value as a float by keys."
	for key in keys:
		defaultFloat = getEvaluatedFloatDefault(defaultFloat, key, xmlElement)
	return defaultFloat

def getEvaluatedFloatDefault(defaultFloat, key, xmlElement=None):
	"Get the evaluated value as a float."
	evaluatedFloat = getEvaluatedFloat(key, xmlElement)
	if evaluatedFloat == None:
		return defaultFloat
	return evaluatedFloat

def getEvaluatedInt(key, xmlElement=None):
	"Get the evaluated value as an int."
	if xmlElement == None:
		return None
	if key in xmlElement.attributeDictionary:
		try:
			return getIntFromFloatString(getEvaluatedValueObliviously(key, xmlElement))
		except:
			print('Warning, could not evaluate the int.')
			print(key)
			print(xmlElement.attributeDictionary[key])
	return None

def getEvaluatedIntByKeys(defaultInt, keys, xmlElement):
	"Get the evaluated value as an int by keys."
	for key in keys:
		defaultInt = getEvaluatedIntDefault(defaultInt, key, xmlElement)
	return defaultInt

def getEvaluatedIntDefault(defaultInt, key, xmlElement=None):
	"Get the evaluated value as an int."
	evaluatedInt = getEvaluatedInt(key, xmlElement)
	if evaluatedInt == None:
		return defaultInt
	return evaluatedInt

def getEvaluatedLinkValue(word, xmlElement):
	"Get the evaluated link value."
	if word == '':
		return None
	if getStartsWithCurlyEqualRoundSquare(word):
		return getEvaluatedExpressionValue(word, xmlElement)
	return word

def getEvaluatedString(key, xmlElement=None):
	"Get the evaluated value as a string."
	if xmlElement == None:
		return None
	if key in xmlElement.attributeDictionary:
		return str(getEvaluatedValueObliviously(key, xmlElement))
	return None

def getEvaluatedStringDefault(defaultString, key, xmlElement=None):
	"Get the evaluated value as a string."
	evaluatedString = getEvaluatedString(key, xmlElement)
	if evaluatedString == None:
		return defaultString
	return evaluatedString

def getEvaluatedValue(key, xmlElement=None):
	"Get the evaluated value."
	if xmlElement == None:
		return None
	if key in xmlElement.attributeDictionary:
		return getEvaluatedValueObliviously(key, xmlElement)
	return None

def getEvaluatedValueObliviously(key, xmlElement):
	"Get the evaluated value."
	value = str(xmlElement.attributeDictionary[key]).strip()
	if key == 'id' or key == 'name':
		return value
	return getEvaluatedLinkValue(value, xmlElement)

def getEvaluator(evaluators, nextWord, word, xmlElement):
	"Get the evaluator."
	global globalSplitDictionary
	if word in globalSplitDictionary:
		return globalSplitDictionary[word](word, xmlElement)
	firstCharacter = word[: 1]
	if firstCharacter == "'" or firstCharacter == '"':
		if len(word) > 1:
			if firstCharacter == word[-1]:
				return EvaluatorValue(word[1 : -1])
	if firstCharacter == '$':
		return EvaluatorValue(word[1 :])
	dotIndex = word.find('.')
	if dotIndex > -1 and len(word) > 1:
		if dotIndex == 0 and word[1].isalpha():
			return EvaluatorAttribute(word, xmlElement)
		if dotIndex > 0:
			untilDot = word[: dotIndex]
			if untilDot in globalModuleEvaluatorDictionary:
				return globalModuleEvaluatorDictionary[untilDot](word, xmlElement)
	if firstCharacter.isalpha() or firstCharacter == '_':
		functions = xmlElement.getXMLProcessor().functions
		if len(functions) > 0:
			if word in functions[-1].localDictionary:
				return EvaluatorLocal(word, xmlElement)
		functionElement = xmlElement.getXMLElementByImportID(word)
		if functionElement != None:
			if functionElement.className == 'function':
				return EvaluatorFunction( word, functionElement )
		return EvaluatorValue(word)
	return EvaluatorNumeric(word, xmlElement)

def getEvaluatorSplitWords(value):
	"Get split words for evaluators."
	if value.startswith('='):
		value = value[len('=') :]
	if len(value) < 1:
		return []
	global globalDictionaryOperatorBegin
	uniqueQuoteIndex = 0
	word = ''
	quoteString = None
	quoteDictionary = {}
	for characterIndex in xrange(len(value)):
		character = value[characterIndex]
		if character == '"' or character == "'":
			if quoteString == None:
				quoteString = ''
			elif quoteString != None:
				if character == quoteString[: 1]:
					uniqueQuoteIndex = getUniqueQuoteIndex(uniqueQuoteIndex, value)
					uniqueToken = getTokenByNumber(uniqueQuoteIndex)
					quoteDictionary[uniqueToken] = quoteString + character
					character = uniqueToken
					quoteString = None
		if quoteString == None:
			word += character
		else:
			quoteString += character
	beginSplitWords = getDictionarySplitWords(globalDictionaryOperatorBegin, word)
	global globalSplitDictionaryOperator
	evaluatorSplitWords = []
	for beginSplitWord in beginSplitWords:
		if beginSplitWord in globalDictionaryOperatorBegin:
			evaluatorSplitWords.append(beginSplitWord)
		else:
			evaluatorSplitWords += getDictionarySplitWords(globalSplitDictionaryOperator, beginSplitWord)
	for evaluatorSplitWordIndex, evaluatorSplitWord in enumerate(evaluatorSplitWords):
		for quoteDictionaryKey in quoteDictionary.keys():
			if quoteDictionaryKey in evaluatorSplitWord:
				evaluatorSplitWords[evaluatorSplitWordIndex] = evaluatorSplitWord.replace(quoteDictionaryKey, quoteDictionary[quoteDictionaryKey])
	evaluatorTransitionWords = []
	for evaluatorSplitWord in evaluatorSplitWords:
		addQuoteWord(evaluatorTransitionWords, evaluatorSplitWord)
	evaluatorSplitWords = []
	for evaluatorTransitionWord in evaluatorTransitionWords:
		addAttributeWord(evaluatorSplitWords, evaluatorTransitionWord)
	return evaluatorSplitWords

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
		evaluatedFloat = euclidean.getFloatFromValue(word)
		if evaluatedFloat != None:
			floatList.append( evaluatedFloat )
	return floatList

def getFloatListListsByPaths(paths):
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

def getKeys(repository):
	'Get keys for repository.'
	repositoryClass = repository.__class__
	if repositoryClass == list or repositoryClass == tuple:
		return range(len(repository))
	if repositoryClass == dict:
		return repository.keys()
	return None

def getIntFromFloatString(value):
	"Get the int from the string."
	floatString = str(value).strip()
	if floatString == '':
		return None
	dotIndex = floatString.find('.')
	if dotIndex < 0:
		return int(value)
	return int( round( float(floatString) ) )

def getIsBracketed(word):
	"Determine if the word is bracketed."
	if len(word) < 2:
		return False
	firstCharacter = word[0]
	lastCharacter = word[-1]
	if firstCharacter == '(' and lastCharacter == ')':
		return True
	return firstCharacter == '[' and lastCharacter == ']'

def getIsQuoted(word):
	"Determine if the word is quoted."
	if len(word) < 2:
		return False
	firstCharacter = word[0]
	lastCharacter = word[-1]
	if firstCharacter == '"' and lastCharacter == '"':
		return True
	return firstCharacter == "'" and lastCharacter == "'"

def getLayerThickness(xmlElement):
	"Get the layer thickness."
	if xmlElement == None:
		return 0.4
	return xmlElement.getCascadeFloat(0.4, 'layerThickness')

def getMatchingPlugins( namePathDictionary, xmlElement ):
	"Get the plugins whose names are in the attribute dictionary."
	matchingPlugins = []
	namePathDictionaryCopy = namePathDictionary.copy()
	for key in xmlElement.attributeDictionary:
		dotIndex = key.find('.')
		if dotIndex > - 1:
			keyUntilDot = key[: dotIndex]
			if keyUntilDot in namePathDictionaryCopy:
				pluginModule = archive.getModuleWithPath( namePathDictionaryCopy[ keyUntilDot ] )
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

def getOverhangSpan(xmlElement):
	"Get the overhang span."
	return xmlElement.getCascadeFloat(0.0, 'overhangSpan')

def getOverhangSupportAngle(xmlElement):
	"Get the overhang support angle in radians."
	return math.radians(xmlElement.getCascadeFloat(45.0, 'overhangSupportAngle'))

def getPathByKey(key, xmlElement):
	"Get path from prefix and xml element."
	if key not in xmlElement.attributeDictionary:
		return []
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue(word, xmlElement)
	if evaluatedLinkValue.__class__ == list:
		return getPathByList(evaluatedLinkValue)
	xmlElementObject = getXMLElementObject(evaluatedLinkValue)
	if xmlElementObject == None:
		return []
	return xmlElementObject.getPaths()[0]

def getPathByList( vertexList ):
	"Get the paths by list."
	if len( vertexList ) < 1:
		return Vector3()
	if vertexList[0].__class__ != list:
		vertexList = [ vertexList ]
	path = []
	for floatList in vertexList:
		vector3 = getVector3ByFloatList( floatList, Vector3() )
		path.append(vector3)
	return path

def getPathByPrefix(path, prefix, xmlElement):
	"Get path from prefix and xml element."
	if len(path) < 2:
		print('Warning, bug, path is too small in evaluate in setPathByPrefix.')
		return
	pathByKey = getPathByKey( prefix + 'path', xmlElement )
	if len( pathByKey ) < len(path):
		for pointIndex in xrange( len( pathByKey ) ):
			path[ pointIndex ] = pathByKey[ pointIndex ]
	else:
		path = pathByKey
	path[0] = getVector3ByPrefix( prefix + 'pathStart', path[0], xmlElement )
	path[-1] = getVector3ByPrefix( prefix + 'pathEnd', path[-1], xmlElement )
	return path

def getPathsByKey(key, xmlElement):
	"Get paths by key."
	if key not in xmlElement.attributeDictionary:
		return []
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue(word, xmlElement)
	if evaluatedLinkValue.__class__ == dict or evaluatedLinkValue.__class__ == list:
		convertToPaths(evaluatedLinkValue)
		return getPathsByLists(evaluatedLinkValue)
	xmlElementObject = getXMLElementObject(evaluatedLinkValue)
	if xmlElementObject == None:
		return []
	return xmlElementObject.getPaths()

def getPathsByKeys(keys, xmlElement):
	"Get paths by keys."
	pathsByKeys = []
	for key in keys:
		pathsByKeys += getPathsByKey(key, xmlElement)
	return pathsByKeys

def getPathsByLists(vertexLists):
	"Get paths by lists."
	vector3Lists = getVector3ListsRecursively(vertexLists)
	paths = []
	addToPathsRecursively(paths, vector3Lists)
	return paths

def getPrecision(xmlElement):
	"Get the cascade precision."
	return xmlElement.getCascadeFloat(0.1, 'precision')

def getSheetThickness(xmlElement):
	"Get the sheet thickness."
	return xmlElement.getCascadeFloat(3.0, 'sheetThickness')

def getSidesBasedOnPrecision(radius, xmlElement):
	"Get the number of poygon sides."
	return int(math.ceil(math.sqrt(0.5 * radius * math.pi * math.pi / getPrecision(xmlElement))))

def getSidesMinimumThreeBasedOnPrecision(radius, xmlElement):
	"Get the number of poygon sides, with a minimum of three."
	return max(getSidesBasedOnPrecision(radius, xmlElement), 3)

def getSidesMinimumThreeBasedOnPrecisionSides(radius, xmlElement):
	"Get the number of poygon sides, with a minimum of three."
	sides = getSidesMinimumThreeBasedOnPrecision(radius, xmlElement)
	return getEvaluatedFloatDefault(sides, 'sides', xmlElement)

def getSplitDictionary():
	"Get split dictionary."
	global globalSplitDictionaryOperator
	splitDictionary = globalSplitDictionaryOperator.copy()
	global globalDictionaryOperatorBegin
	splitDictionary.update( globalDictionaryOperatorBegin )
	splitDictionary['and'] = EvaluatorAnd
	splitDictionary['false'] = EvaluatorFalse
	splitDictionary['False'] = EvaluatorFalse
	splitDictionary['or'] = EvaluatorOr
	splitDictionary['not'] = EvaluatorNot
	splitDictionary['true'] = EvaluatorTrue
	splitDictionary['True'] = EvaluatorTrue
	splitDictionary['none'] = EvaluatorNone
	splitDictionary['None'] = EvaluatorNone
	return splitDictionary

def getStartsWithCurlyEqualRoundSquare(word):
	"Determine if the word starts with round or square brackets."
	return word.startswith('{') or word.startswith('=') or word.startswith('(') or word.startswith('[')

def getTokenByNumber(number):
	"Get token by number."
	return '_%s_' % number

def getTransformedPathByKey(key, xmlElement):
	"Get transformed path from prefix and xml element."
	if key not in xmlElement.attributeDictionary:
		return []
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue(word, xmlElement)
	if evaluatedLinkValue.__class__ == list:
		return getPathByList(evaluatedLinkValue)
	xmlElementObject = getXMLElementObject(evaluatedLinkValueClass)
	if xmlElementObject == None:
		return []
	return xmlElementObject.getTransformedPaths()[0]

def getTransformedPathByPrefix(path, prefix, xmlElement):
	"Get path from prefix and xml element."
	if len(path) < 2:
		print('Warning, bug, path is too small in evaluate in setPathByPrefix.')
		return
	pathByKey = getTransformedPathByKey( prefix + 'path', xmlElement )
	if len( pathByKey ) < len(path):
		for pointIndex in xrange( len( pathByKey ) ):
			path[ pointIndex ] = pathByKey[ pointIndex ]
	else:
		path = pathByKey
	path[0] = getVector3ByPrefix( prefix + 'pathStart', path[0], xmlElement )
	path[-1] = getVector3ByPrefix( prefix + 'pathEnd', path[-1], xmlElement )
	return path

def getTransformedPathsByKey(key, xmlElement):
	"Get transformed paths by key."
	if key not in xmlElement.attributeDictionary:
		return []
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue(word, xmlElement)
	if evaluatedLinkValue.__class__ == dict or evaluatedLinkValue.__class__ == list:
		convertToTransformedPaths(evaluatedLinkValue)
		return getPathsByLists(evaluatedLinkValue)
	xmlElementObject = getXMLElementObject(evaluatedLinkValue)
	if xmlElementObject == None:
		return []
	return xmlElementObject.getTransformedPaths()

def getUniqueQuoteIndex( uniqueQuoteIndex, word ):
	"Get uniqueQuoteIndex."
	uniqueQuoteIndex += 1
	while getTokenByNumber(uniqueQuoteIndex) in word:
		uniqueQuoteIndex += 1
	return uniqueQuoteIndex

def getUniqueToken(word):
	'Get unique token.'
	uniqueString = '@#!'
	for character in uniqueString:
		if character not in word:
			return character
	uniqueNumber = 0
	while True:
		for character in uniqueString:
			uniqueToken = character + str(uniqueNumber)
			if uniqueToken not in word:
				return uniqueToken
			uniqueNumber += 1

def getVector3ByDictionary( dictionary, vector3 ):
	"Get vector3 by dictionary."
	if 'x' in dictionary:
		vector3 = getVector3IfNone(vector3)
		vector3.x = euclidean.getFloatFromValue(dictionary['x'])
	if 'y' in dictionary:
		vector3 = getVector3IfNone(vector3)
		vector3.y = euclidean.getFloatFromValue(dictionary['y'])
	if 'z' in dictionary:
		vector3 = getVector3IfNone(vector3)
		vector3.z = euclidean.getFloatFromValue( dictionary['z'] )
	return vector3

def getVector3ByDictionaryListValue(value, vector3):
	"Get vector3 by dictionary, list or value."
	if value.__class__ == Vector3 or value.__class__.__name__ == 'Vector3Index':
		return value
	if value.__class__ == dict:
		return getVector3ByDictionary(value, vector3)
	if value.__class__ == list:
		return getVector3ByFloatList(value, vector3)
	floatFromValue = euclidean.getFloatFromValue(value)
	if floatFromValue ==  None:
		return vector3
	vector3.setToXYZ(floatFromValue, floatFromValue, floatFromValue)
	return vector3

def getVector3ByFloatList(floatList, vector3):
	"Get vector3 by float list."
	if len(floatList) > 0:
		vector3 = getVector3IfNone(vector3)
		vector3.x = euclidean.getFloatFromValue(floatList[0])
	if len(floatList) > 1:
		vector3 = getVector3IfNone(vector3)
		vector3.y = euclidean.getFloatFromValue(floatList[1])
	if len(floatList) > 2:
		vector3 = getVector3IfNone(vector3)
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

def getVector3ByPrefix(prefix, vector3, xmlElement):
	"Get vector3 from prefix and xml element."
	value = getEvaluatedValue(prefix, xmlElement)
	if value != None:
		vector3 = getVector3ByDictionaryListValue(value, vector3)
	x = getEvaluatedFloat(prefix + '.x', xmlElement)
	if x != None:
		vector3 = getVector3IfNone(vector3)
		vector3.x = x
	y = getEvaluatedFloat(prefix + '.y', xmlElement)
	if y != None:
		vector3 = getVector3IfNone(vector3)
		vector3.y = y
	z = getEvaluatedFloat(prefix + '.z', xmlElement)
	if z != None:
		vector3 = getVector3IfNone(vector3)
		vector3.z = z
	return vector3

def getVector3ByPrefixes( prefixes, vector3, xmlElement ):
	"Get vector3 from prefixes and xml element."
	for prefix in prefixes:
		vector3 = getVector3ByPrefix(prefix, vector3, xmlElement)
	return vector3

def getVector3FromXMLElement(xmlElement):
	"Get vector3 from xml element."
	vector3 = Vector3(
		getEvaluatedFloatDefault(0.0, 'x', xmlElement),
		getEvaluatedFloatDefault(0.0, 'y', xmlElement),
		getEvaluatedFloatDefault(0.0, 'z', xmlElement))
	return getCumulativeVector3('', vector3, xmlElement)

def getVector3IfNone(vector3):
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

def getVector3RemoveByPrefix(prefix, vector3, xmlElement):
	"Get vector3 from prefix and xml element, then remove prefix attributes from dictionary."
	vector3RemoveByPrefix = getVector3ByPrefix(prefix, vector3, xmlElement)
	euclidean.removePrefixFromDictionary( xmlElement.attributeDictionary, prefix )
	return vector3RemoveByPrefix

def getVisibleObjects(archivableObjects):
	"Get the visible objects."
	visibleObjects = []
	for archivableObject in archivableObjects:
		if archivableObject.getVisible():
			visibleObjects.append(archivableObject)
	return visibleObjects

def getXMLElementByKey(key, xmlElement):
	"Get the xml element by key."
	if key not in xmlElement.attributeDictionary:
		return None
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue(word, xmlElement)
	if evaluatedLinkValue.__class__.__name__ == 'XMLElement':
		return evaluatedLinkValue
	print('Warning, could not get XMLElement in getXMLElementByKey in evaluate for:')
	print(key)
	print(evaluatedLinkValue)
	print(xmlElement)
	return None

def getXMLElementObject(evaluatedLinkValue):
	"Get XMLElementObject."
	if evaluatedLinkValue.__class__.__name__ != 'XMLElement':
		print('Warning, could not get XMLElement in getXMLElementObject in evaluate for:')
		print(evaluatedLinkValue)
		return None
	if evaluatedLinkValue.object == None:
		print('Warning, evaluatedLinkValue.object is None in getXMLElementObject in evaluate for:')
		print(evaluatedLinkValue)
		return None
	return evaluatedLinkValue.object

def getXMLElementsByKey(key, xmlElement):
	"Get the xml elements by key."
	if key not in xmlElement.attributeDictionary:
		return []
	word = str(xmlElement.attributeDictionary[key]).strip()
	evaluatedLinkValue = getEvaluatedLinkValue(word, xmlElement)
	if evaluatedLinkValue.__class__.__name__ == 'XMLElement':
		return [evaluatedLinkValue]
	if evaluatedLinkValue.__class__ == list:
		return evaluatedLinkValue
	print('Warning, could not get XMLElements in getXMLElementsByKey in evaluate for:')
	print(key)
	print(evaluatedLinkValue)
	print(xmlElement)
	return None

def processArchivable(archivableClass, xmlElement):
	"Get any new elements and process the archivable."
	if xmlElement == None:
		return
	getArchivableObjectAddToParent(archivableClass, xmlElement)
	xmlElement.getXMLProcessor().processChildren(xmlElement)

def processCondition(xmlElement):
	"Process the xml element condition."
	xmlProcessor = xmlElement.getXMLProcessor()
	if xmlElement.object == None:
		xmlElement.object = ModuleXMLElement(xmlElement)
	if xmlElement.object.conditionSplitWords == None:
		return
	if len(xmlProcessor.functions ) < 1:
		print('Warning, "in" element is not in a function in processCondition in evaluate for:')
		print(xmlElement)
		return
	if int( getEvaluatedExpressionValueBySplitLine( xmlElement.object.conditionSplitWords, xmlElement ) ) > 0:
		xmlProcessor.functions[-1].processChildren(xmlElement)
	else:
		xmlElement.object.processElse(xmlElement)

def setAttributeDictionaryByArguments(argumentNames, arguments, xmlElement):
	"Set the attribute dictionary to the arguments."
	for argumentIndex, argument in enumerate(arguments):
		xmlElement.attributeDictionary[argumentNames[argumentIndex]] = argument


class Evaluator:
	'Base evaluator class.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.value = None
		self.word = word

	def __repr__(self):
		"Get the string representation of this Evaluator."
		return '%s: %s, %s' % ( self.__class__.__name__, self.word, self.value )

	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		pass

	def executeCenterOperation(self, evaluators, evaluatorIndex):
		'Execute operator which acts on the center.'
		pass

	def executeDictionary(self, dictionary, evaluators, keys, evaluatorIndex, nextEvaluator):
		'Execute the dictionary.'
		del evaluators[evaluatorIndex]
		enumeratorKeys = euclidean.getEnumeratorKeys(dictionary, keys)
		if enumeratorKeys.__class__ == list:
			nextEvaluator.value = []
			for enumeratorKey in enumeratorKeys:
				if enumeratorKey in dictionary:
					nextEvaluator.value.append(dictionary[enumeratorKey])
				else:
					print('Warning, key in executeKey in Evaluator in evaluate is not in for:')
					print(enumeratorKey)
					print(dictionary)
			return
		if enumeratorKeys in dictionary:
			nextEvaluator.value = dictionary[enumeratorKeys]
		else:
			print('Warning, key in executeKey in Evaluator in evaluate is not in for:')
			print(enumeratorKeys)
			print(dictionary)

	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		pass

	def executeKey(self, evaluators, keys, evaluatorIndex, nextEvaluator):
		'Execute the key index.'
		if self.value.__class__ == str:
			self.executeString(evaluators, keys, evaluatorIndex, nextEvaluator)
			return
		if self.value.__class__ == list:
			self.executeList(evaluators, keys, evaluatorIndex, nextEvaluator)
			return
		if self.value.__class__ == dict:
			self.executeDictionary(self.value, evaluators, keys, evaluatorIndex, nextEvaluator)
			return
		getAccessibleDictionaryFunction = getattr(self.value, '_getAccessibleDictionary', None)
		if getAccessibleDictionaryFunction != None:
			self.executeDictionary(getAccessibleDictionaryFunction(), evaluators, keys, evaluatorIndex, nextEvaluator)
			return
		if self.value.__class__.__name__ != 'XMLElement':
			return
		del evaluators[evaluatorIndex]
		enumeratorKeys = euclidean.getEnumeratorKeys(self.value.attributeDictionary, keys)
		if enumeratorKeys.__class__ == list:
			nextEvaluator.value = []
			for enumeratorKey in enumeratorKeys:
				if enumeratorKey in self.value.attributeDictionary:
					nextEvaluator.value.append(getEvaluatedExpressionValue(self.value.attributeDictionary[enumeratorKey], self.value))
				else:
					print('Warning, key in executeKey in Evaluator in evaluate is not in for:')
					print(enumeratorKey)
					print(self.value.attributeDictionary)
			return
		if enumeratorKeys in self.value.attributeDictionary:
			nextEvaluator.value = getEvaluatedExpressionValue(self.value.attributeDictionary[enumeratorKeys], self.value)
		else:
			print('Warning, key in executeKey in Evaluator in evaluate is not in for:')
			print(enumeratorKeys)
			print(self.value.attributeDictionary)

	def executeLeftOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Execute operator which acts from the left.'
		pass

	def executeList(self, evaluators, keys, evaluatorIndex, nextEvaluator):
		'Execute the key index.'
		del evaluators[evaluatorIndex]
		enumeratorKeys = euclidean.getEnumeratorKeys(self.value, keys)
		if enumeratorKeys.__class__ == list:
			nextEvaluator.value = []
			for enumeratorKey in enumeratorKeys:
				intKey = euclidean.getIntFromValue(enumeratorKey)
				if self.getIsInRange(intKey):
					nextEvaluator.value.append(self.value[intKey])
				else:
					print('Warning, key in executeList in Evaluator in evaluate is not in for:')
					print(enumeratorKey)
					print(self.value)
			return
		intKey = euclidean.getIntFromValue(enumeratorKeys)
		if self.getIsInRange(intKey):
			nextEvaluator.value = self.value[intKey]
		else:
			print('Warning, key in executeList in Evaluator in evaluate is not in for:')
			print(enumeratorKeys)
			print(self.value)

	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		pass

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Execute operator which acts from the right.'
		pass

	def executeString(self, evaluators, keys, evaluatorIndex, nextEvaluator):
		'Execute the string.'
		del evaluators[evaluatorIndex]
		enumeratorKeys = euclidean.getEnumeratorKeys(self.value, keys)
		if enumeratorKeys.__class__ == list:
			nextEvaluator.value = ''
			for enumeratorKey in enumeratorKeys:
				intKey = euclidean.getIntFromValue(enumeratorKey)
				if self.getIsInRange(intKey):
					nextEvaluator.value += self.value[intKey]
				else:
					print('Warning, key in executeString in Evaluator in evaluate is not in for:')
					print(enumeratorKey)
					print(self.value)
			return
		intKey = euclidean.getIntFromValue(enumeratorKeys)
		if self.getIsInRange(intKey):
			nextEvaluator.value = self.value[intKey]
		else:
			print('Warning, key in executeString in Evaluator in evaluate is not in for:')
			print(enumeratorKeys)
			print(self.value)

	def getIsInRange(self, keyIndex):
		'Determine if the keyIndex is in range.'
		if keyIndex == None:
			return False
		return keyIndex >= -len(self.value) and keyIndex < len(self.value)


class EvaluatorAddition(Evaluator):
	'Class to add two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel == 20:
			self.executePair(evaluators, evaluatorIndex)

	def executePair( self, evaluators, evaluatorIndex ):
		'Add two evaluators.'
		leftIndex = evaluatorIndex - 1
		rightIndex = evaluatorIndex + 1
		if leftIndex < 0:
			print('Warning, no leftKey in executePair in EvaluatorAddition for:')
			print(evaluators)
			print(evaluatorIndex)
			print(self)
			del evaluators[evaluatorIndex]
			return
		if rightIndex >= len(evaluators):
			print('Warning, no rightKey in executePair in EvaluatorAddition for:')
			print(evaluators)
			print(evaluatorIndex)
			print(self)
			del evaluators[evaluatorIndex]
			return
		rightValue = evaluators[rightIndex].value
		evaluators[leftIndex].value = self.getOperationValue(evaluators[leftIndex].value, evaluators[rightIndex].value)
		del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]

	def getEvaluatedValues(self, enumerable, keys, value):
		'Get evaluatedValues.'
		if enumerable.__class__ == dict:
			evaluatedValues = {}
			for key in keys:
				evaluatedValues[key] = self.getOperationValue(value, enumerable[key])
			return evaluatedValues
		evaluatedValues = []
		for key in keys:
			evaluatedValues.append(self.getOperationValue(value, enumerable[key]))
		return evaluatedValues

	def getOperationValue(self, leftValue, rightValue):
		'Get operation value.'
		leftKeys = getKeys(leftValue)
		rightKeys = getKeys(rightValue)
		if leftKeys == None and rightKeys == None:
			return self.getValueFromValuePair(leftValue, rightValue)
		if leftKeys == None:
			return self.getEvaluatedValues(rightValue, rightKeys, leftValue)
		if rightKeys == None:
			return self.getEvaluatedValues(leftValue, leftKeys, rightValue)
		if leftKeys != rightKeys:
			print('Warning, the leftKeys are different from the rightKeys in getOperationValue in EvaluatorAddition for:')
			print('leftValue')
			print(leftValue)
			print(leftKeys)
			print('rightValue')
			print(rightValue)
			print(rightKeys)
			print(self)
			return None
		if leftValue.__class__ == dict or rightValue.__class__ == dict:
			evaluatedValues = {}
			for leftKey in leftKeys:
				evaluatedValues[leftKey] = self.getOperationValue(leftValue[leftKey], rightValue[leftKey])
			return evaluatedValues
		evaluatedValues = []
		for leftKey in leftKeys:
			evaluatedValues.append(self.getOperationValue(leftValue[leftKey], rightValue[leftKey]))
		return evaluatedValues

	def getValueFromValuePair(self, leftValue, rightValue):
		'Add two values.'
		return leftValue + rightValue


class EvaluatorEqual(EvaluatorAddition):
	'Class to compare two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel == 15:
			self.executePair(evaluators, evaluatorIndex)

	def getBooleanFromValuePair(self, leftValue, rightValue):
		'Compare two values.'
		return leftValue == rightValue

	def getValueFromValuePair(self, leftValue, rightValue):
		'Get value from comparison.'
		return self.getBooleanFromValuePair(leftValue, rightValue)


class EvaluatorSubtraction(EvaluatorAddition):
	'Class to subtract two evaluators.'
	def executeLeft( self, evaluators, evaluatorIndex ):
		'Minus the value to the right.'
		leftIndex = evaluatorIndex - 1
		rightIndex = evaluatorIndex + 1
		leftValue = None
		if leftIndex >= 0:
			leftValue = evaluators[leftIndex].value
		if leftValue != None:
			return
		rightValue = evaluators[rightIndex].value
		if rightValue == None:
			print('Warning, can not minus.')
			print( evaluators[rightIndex].word )
		else:
			evaluators[rightIndex].value = self.getNegativeValue(rightValue)
		del evaluators[evaluatorIndex]

	def executeLeftOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Minus the value to the right.'
		if operationLevel == 200:
			self.executeLeft(evaluators, evaluatorIndex)

	def getNegativeValue( self, value ):
		'Get the negative value.'
		keys = getKeys(value)
		if keys == None:
			return self.getValueFromSingleValue(value)
		for key in keys:
			value[key] = self.getNegativeValue(value[key])
		return value

	def getValueFromSingleValue( self, value ):
		'Minus value.'
		return -value

	def getValueFromValuePair(self, leftValue, rightValue):
		'Subtract two values.'
		return leftValue - rightValue


class EvaluatorAnd(EvaluatorAddition):
	'Class to compare two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel == 12:
			self.executePair(evaluators, evaluatorIndex)

	def getBooleanFromValuePair(self, leftValue, rightValue):
		'And two values.'
		return leftValue and rightValue

	def getValueFromValuePair(self, leftValue, rightValue):
		'Get value from comparison.'
		return self.getBooleanFromValuePair(leftValue, rightValue)


class EvaluatorAttribute(Evaluator):
	'Class to handle an attribute.'
	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		if self.value == None:
			print('Warning, executeFunction in EvaluatorAttribute in evaluate can not get a self.value for:')
			print(evaluatorIndex)
			print(evaluators)
			print(self)
			return
		nextEvaluator.value = self.value(*nextEvaluator.arguments)
		del evaluators[evaluatorIndex]

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Execute operator which acts from the right.'
		attributeName = self.word[1 :]
		previousIndex = evaluatorIndex - 1
		previousEvaluator = evaluators[previousIndex]
		if previousEvaluator.value.__class__ == dict:
			from fabmetheus_utilities.geometry.geometry_utilities.evaluate_enumerables import dictionary_attribute
			self.value = dictionary_attribute._getAccessibleAttribute(attributeName, previousEvaluator.value)
		elif previousEvaluator.value.__class__ == list:
			from fabmetheus_utilities.geometry.geometry_utilities.evaluate_enumerables import list_attribute
			self.value = list_attribute._getAccessibleAttribute(attributeName, previousEvaluator.value)
		elif previousEvaluator.value.__class__ == str:
			from fabmetheus_utilities.geometry.geometry_utilities.evaluate_enumerables import string_attribute
			self.value = string_attribute._getAccessibleAttribute(attributeName, previousEvaluator.value)
		else:
			self.value = getattr(previousEvaluator.value, '_getAccessibleAttribute', None)(attributeName)
		if self.value == None:
			print('Warning, EvaluatorAttribute in evaluate can not get a getAccessibleAttributeFunction for:')
			print(attributeName)
			print(previousEvaluator.value)
			print(self)
			return
		del evaluators[previousIndex]


class EvaluatorBracketCurly(Evaluator):
	'Class to evaluate a string.'
	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		for evaluatorIndex in xrange( bracketEndIndex - 3, bracketBeginIndex, - 1 ):
			bracketEndIndex = getEndIndexConvertEquationValue( bracketEndIndex, evaluatorIndex, evaluators )
		evaluatedExpressionValueEvaluators = getBracketEvaluators(bracketBeginIndex, bracketEndIndex, evaluators)
		self.value = {}
		for evaluatedExpressionValueEvaluator in evaluatedExpressionValueEvaluators:
			keyValue = evaluatedExpressionValueEvaluator.value
			self.value[ keyValue.keyTuple[0] ] = keyValue.keyTuple[1]
		del evaluators[ bracketBeginIndex + 1: bracketEndIndex + 1 ]


class EvaluatorBracketRound(Evaluator):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.arguments = []
		self.value = None
		self.word = word

	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		self.arguments = getBracketValuesDeleteEvaluator(bracketBeginIndex, bracketEndIndex, evaluators)
		if len( self.arguments ) < 1:
			return
		if len( self.arguments ) > 1:
			self.value = self.arguments
		else:
			self.value = self.arguments[0]

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Evaluate the statement and delete the evaluators.'
		previousIndex = evaluatorIndex - 1
		if previousIndex < 0:
			return
		evaluators[ previousIndex ].executeFunction( evaluators, previousIndex, self )


class EvaluatorBracketSquare(Evaluator):
	'Class to evaluate a string.'
	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		self.value = getBracketValuesDeleteEvaluator(bracketBeginIndex, bracketEndIndex, evaluators)

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Evaluate the statement and delete the evaluators.'
		previousIndex = evaluatorIndex - 1
		if previousIndex < 0:
			return
		if self.value.__class__ != list:
			return
		evaluators[ previousIndex ].executeKey( evaluators, self.value, previousIndex, self )


class EvaluatorComma(Evaluator):
	'Class to join two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel != 0:
			return
		previousIndex = evaluatorIndex - 1
		if previousIndex < 0:
			evaluators[evaluatorIndex].value = None
			return
		if evaluators[previousIndex].word == ',':
			evaluators[evaluatorIndex].value = None
			return
		del evaluators[evaluatorIndex]


class EvaluatorConcatenate(Evaluator):
	'Class to join two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel != 80:
			return
		leftIndex = evaluatorIndex - 1
		if leftIndex < 0:
			del evaluators[evaluatorIndex]
			return
		rightIndex = evaluatorIndex + 1
		if rightIndex >= len(evaluators):
			del evaluators[ leftIndex : rightIndex ]
			return
		leftValue = evaluators[leftIndex].value
		rightValue = evaluators[rightIndex].value
		if leftValue.__class__ == rightValue.__class__ and (leftValue.__class__ == list or rightValue.__class__ == str):
			evaluators[leftIndex].value = leftValue + rightValue
			del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]
			return
		if leftValue.__class__ == list and rightValue.__class__ == int:
			if rightValue > 0:
				originalList = leftValue[:]
				for copyIndex in xrange( rightValue - 1 ):
					leftValue += originalList
				evaluators[leftIndex].value = leftValue
				del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]
			return
		if leftValue.__class__ == dict and rightValue.__class__ == dict:
			leftValue.update(rightValue)
			evaluators[leftIndex].value = leftValue
			del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]
			return
		del evaluators[ leftIndex : evaluatorIndex + 2 ]


class EvaluatorDictionary(Evaluator):
	'Class to join two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel != 10:
			return
		leftEvaluatorIndex = evaluatorIndex - 1
		if leftEvaluatorIndex < 0:
			print('Warning, leftEvaluatorIndex is less than zero in EvaluatorDictionary for:')
			print(self)
			print(evaluators)
			return
		rightEvaluatorIndex = evaluatorIndex + 1
		if rightEvaluatorIndex >= len(evaluators):
			print('Warning, rightEvaluatorIndex too high in EvaluatorDictionary for:')
			print(rightEvaluatorIndex)
			print(self)
			print(evaluators)
			return
		evaluators[rightEvaluatorIndex].value = KeyValue(evaluators[leftEvaluatorIndex].value, evaluators[rightEvaluatorIndex].value)
		del evaluators[ leftEvaluatorIndex : rightEvaluatorIndex ]


class EvaluatorDivision(EvaluatorAddition):
	'Class to divide two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel == 40:
			self.executePair(evaluators, evaluatorIndex)

	def getValueFromValuePair(self, leftValue, rightValue):
		'Divide two values.'
		return leftValue / rightValue


class EvaluatorElement(Evaluator):
	'Element evaluator class.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.value = None
		self.word = word
		self.xmlElement = xmlElement

	def executeCenterOperation(self, evaluators, evaluatorIndex):
		'Execute operator which acts on the center.'
		dotIndex = self.word.find('.')
		if dotIndex < 0:
			print('Warning, EvaluatorElement in evaluate can not find the dot for:')
			print(functionName)
			print(self)
			return
		attributeName = self.word[dotIndex + 1 :]
		moduleName = self.word[: dotIndex]
		if moduleName in globalModuleFunctionsDictionary:
			self.value = globalModuleFunctionsDictionary[moduleName](attributeName, self.xmlElement)
			return
		pluginModule = None
		if moduleName in globalElementNameSet:
			pluginModule = archive.getModuleWithPath(archive.getElementsPath(moduleName))
		if pluginModule == None:
			print('Warning, EvaluatorElement in evaluate can not get a pluginModule for:')
			print(moduleName)
			print(self)
			return
		getAccessibleAttributeFunction = pluginModule._getAccessibleAttribute
		globalModuleFunctionsDictionary[moduleName] = getAccessibleAttributeFunction
		self.value = getAccessibleAttributeFunction(attributeName, self.xmlElement)

	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		if self.value == None:
			print('Warning, executeFunction in EvaluatorElement in evaluate can not get a self.value for:')
			print(evaluatorIndex)
			print(evaluators)
			print(self)
			return
		nextEvaluator.value = self.value(*nextEvaluator.arguments)
		del evaluators[evaluatorIndex]


class EvaluatorFalse(Evaluator):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value to zero.'
		self.value = False
		self.word = word


class EvaluatorFunction(Evaluator):
	'Function evaluator class.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.value = None
		self.word = word
		self.xmlElement = xmlElement

	def executeFunction(self, evaluators, evaluatorIndex, nextEvaluator):
		'Execute the function.'
		if self.xmlElement.object == None:
			if 'return' in self.xmlElement.attributeDictionary:
				value = self.xmlElement.attributeDictionary['return']
				self.xmlElement.object = getEvaluatorSplitWords(value)
			else:
				self.xmlElement.object = []
		self.function = Function( self.xmlElement.object, self.xmlElement )
		self.setFunctionLocalTable( nextEvaluator )
		nextEvaluator.value = self.function.getReturnValue()
		del evaluators[evaluatorIndex]

	def setFunctionLocalTable(self, nextEvaluator):
		'Evaluate the function statement and delete the evaluators.'
		self.function.localDictionary['_arguments'] = nextEvaluator.arguments
		if len(nextEvaluator.arguments) > 0:
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
		for parameterWordIndex, parameterWord in enumerate(parameterWords):
			strippedWord = parameterWord.strip()
			keyValue = KeyValue().getByEqual(strippedWord)
			if parameterWordIndex < len(nextEvaluator.arguments):
				self.function.localDictionary[keyValue.keyTuple[0]] = nextEvaluator.arguments[parameterWordIndex]
			else:
				strippedValue = keyValue.keyTuple[1]
				if strippedValue == None:
					print('Warning there is no default parameter in getParameterValue for:')
					print(strippedWord)
					print(parameterWords)
					print(nextEvaluator.arguments)
					print( self.function.xmlElement.attributeDictionary )
				else:
					strippedValue = strippedValue.strip()
				self.function.localDictionary[keyValue.keyTuple[0].strip()] = strippedValue
		if len(nextEvaluator.arguments) > len(parameterWords):
			print('Warning there are too many function parameters for:')
			print( self.function.xmlElement.attributeDictionary )
			print(parameterWords)
			print(nextEvaluator.arguments)


class EvaluatorFundamental(EvaluatorAttribute):
	'Fundamental evaluator class.'
	def executeCenterOperation(self, evaluators, evaluatorIndex):
		'Execute operator which acts on the center.'
		dotIndex = self.word.find('.')
		if dotIndex < 0:
			print('Warning, EvaluatorFundamental in evaluate can not find the dot for:')
			print(functionName)
			print(self)
			return
		attributeName = self.word[dotIndex + 1 :]
		moduleName = self.word[: dotIndex]
		if moduleName in globalModuleFunctionsDictionary:
			self.value = globalModuleFunctionsDictionary[moduleName](attributeName)
			return
		pluginModule = None
		if moduleName in globalFundamentalNameSet:
			pluginModule = archive.getModuleWithPath(archive.getFundamentalsPath(moduleName))
		else:
			underscoredName = '_' + moduleName
			if underscoredName in globalFundamentalNameSet:
				pluginModule = archive.getModuleWithPath(archive.getFundamentalsPath(underscoredName))
		if pluginModule == None:
			print('Warning, EvaluatorFundamental in evaluate can not get a pluginModule for:')
			print(moduleName)
			print(self)
			return
		getAccessibleAttributeFunction = pluginModule._getAccessibleAttribute
		globalModuleFunctionsDictionary[moduleName] = getAccessibleAttributeFunction
		self.value = getAccessibleAttributeFunction(attributeName)


class EvaluatorGreaterEqual( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair(self, leftValue, rightValue):
		'Compare two values.'
		return leftValue >= rightValue


class EvaluatorGreater( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair(self, leftValue, rightValue):
		'Compare two values.'
		return leftValue > rightValue


class EvaluatorLessEqual( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair(self, leftValue, rightValue):
		'Compare two values.'
		return leftValue <= rightValue


class EvaluatorLess( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair(self, leftValue, rightValue):
		'Compare two values.'
		return leftValue < rightValue


class EvaluatorLocal(Evaluator):
	'Class to get a local variable.'
	def __init__(self, word, xmlElement):
		'Set value.'
		self.word = word
		self.value = None
		functions = xmlElement.getXMLProcessor().functions
		if len(functions) < 1:
			return
		localDictionary = functions[-1].localDictionary
		if word in localDictionary:
			self.value = localDictionary[word]


class EvaluatorModulo( EvaluatorDivision ):
	'Class to modulo two evaluators.'
	def getValueFromValuePair(self, leftValue, rightValue):
		'Modulo two values.'
		return leftValue % rightValue


class EvaluatorMultiplication( EvaluatorDivision ):
	'Class to multiply two evaluators.'
	def getValueFromValuePair(self, leftValue, rightValue):
		'Multiply two values.'
		return leftValue * rightValue


class EvaluatorNone(Evaluator):
	'Class to evaluate None.'
	def __init__(self, word, xmlElement):
		'Set value to none.'
		self.value = None
		self.word = str(word)


class EvaluatorNot(EvaluatorSubtraction):
	'Class to compare two evaluators.'
	def executeLeftOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Minus the value to the right.'
		if operationLevel == 13:
			self.executeLeft(evaluators, evaluatorIndex)

	def getValueFromSingleValue( self, value ):
		'Minus value.'
		return not value


class EvaluatorNotEqual( EvaluatorEqual ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair(self, leftValue, rightValue):
		'Compare two values.'
		return leftValue != rightValue


class EvaluatorNumeric(Evaluator):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value.'
		self.value = None
		self.word = word
		try:
			if '.' in word:
				self.value = float(word)
			else:
				self.value = int(word)
		except:
			print('Warning, in EvaluatorNumeric in evaluate could not get a numeric value for:')
			print(word)
			print(xmlElement)


class EvaluatorOr( EvaluatorAnd ):
	'Class to compare two evaluators.'
	def getBooleanFromValuePair(self, leftValue, rightValue):
		'Or two values.'
		return leftValue or rightValue


class EvaluatorPower(EvaluatorAddition):
	'Class to power two evaluators.'
	def executePairOperation(self, evaluators, evaluatorIndex, operationLevel):
		'Operate on two evaluators.'
		if operationLevel == 60:
			self.executePair(evaluators, evaluatorIndex)

	def getValueFromValuePair(self, leftValue, rightValue):
		'Power of two values.'
		return leftValue ** rightValue


class EvaluatorTrue(Evaluator):
	'Class to evaluate a string.'
	def __init__(self, word, xmlElement):
		'Set value to true.'
		self.value = True
		self.word = word


class EvaluatorValue(Evaluator):
	'Class to evaluate a string.'
	def __init__(self, word):
		'Set value to none.'
		self.value = word
		self.word = str(word)


class Function:
	"Class to get equation results."
	def __init__( self, evaluatorSplitLine, xmlElement ):
		"Initialize."
		self.evaluatorSplitLine = evaluatorSplitLine
		self.localDictionary = {}
		self.returnValue = None
		self.xmlElement = xmlElement
		self.xmlProcessor = xmlElement.getXMLProcessor()
		self.xmlProcessor.functions.append(self)

	def __repr__(self):
		"Get the string representation of this Function."
		return '%s, %s, %s' % ( self.evaluatorSplitLine, self.localDictionary, self.returnValue )

	def getReturnValue(self):
		"Get return value."
		self.getReturnValueWithoutDeletion()
		self.reset()
		return self.returnValue

	def getReturnValueWithoutDeletion(self):
		"Get return value without deleting last function."
		if len( self.evaluatorSplitLine ) < 1:
			self.shouldReturn = False
			self.processChildren(self.xmlElement)
		else:
			self.returnValue = getEvaluatedExpressionValueBySplitLine( self.evaluatorSplitLine, self.xmlElement )
		return self.returnValue

	def processChildren(self, xmlElement):
		"Process children if shouldReturn is false."
		for child in xmlElement.children:
			if self.shouldReturn:
				return
			self.xmlProcessor.processXMLElement( child )

	def reset(self):
		"Reset functions."
		del self.xmlElement.getXMLProcessor().functions[-1]


class KeyValue:
	"Class to hold a key value."
	def __init__( self, key = None, value = None ):
		"Get key value."
		if key.__class__ == KeyValue:
			self.keyTuple = key.keyTuple + ( value, )
			return
		self.keyTuple = ( key, value )

	def __repr__(self):
		"Get the string representation of this KeyValue."
		return str( self.keyTuple )

	def getByCharacter( self, character, line ):
		"Get by character."
		dotIndex = line.find( character )
		if dotIndex < 0:
			self.keyTuple = ( line, None )
			return self
		self.keyTuple = ( line[: dotIndex], line[ dotIndex + 1 : ] )
		return self

	def getByDot(self, line):
		"Get by dot."
		return self.getByCharacter('.', line )

	def getByEqual(self, line):
		"Get by dot."
		return self.getByCharacter('=', line )


class ModuleXMLElement:
	"Class to get the in attribute, the index name and the value name."
	def __init__( self, xmlElement):
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
		xmlProcessor = xmlElement.getXMLProcessor()
		if lowerClassName not in xmlProcessor.namePathDictionary:
			return
		self.pluginModule = archive.getModuleWithPath( xmlProcessor.namePathDictionary[ lowerClassName ] )
		if self.pluginModule == None:
			return
		self.elseElement = nextXMLElement

	def processElse( self, xmlElement):
		"Process the else statement."
		if self.elseElement != None:
			self.pluginModule.processElse( self.elseElement)


globalCreationDictionary = archive.getGeometryDictionary('creation')
globalDictionaryOperatorBegin = {
	'||' : EvaluatorConcatenate,
	'==' : EvaluatorEqual,
	'>=' : EvaluatorGreaterEqual,
	'<=' : EvaluatorLessEqual,
	'!=' : EvaluatorNotEqual,
	'**' : EvaluatorPower }
globalModuleEvaluatorDictionary = {}
globalFundamentalNameSet = set(archive.getPluginFileNamesFromDirectoryPath(archive.getFundamentalsPath()))
addPrefixDictionary(globalModuleEvaluatorDictionary, globalFundamentalNameSet, EvaluatorFundamental)
globalElementNameSet = set(archive.getPluginFileNamesFromDirectoryPath(archive.getElementsPath()))
addPrefixDictionary(globalModuleEvaluatorDictionary, globalElementNameSet, EvaluatorElement)
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
