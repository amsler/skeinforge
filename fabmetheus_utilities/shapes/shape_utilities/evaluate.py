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


def getEvaluator( evaluators, nextWord, word, xmlElement ):
	"Get the evaluator."
	global globalSplitDictionary
	if word in globalSplitDictionary:
		return globalSplitDictionary[ word ]( word, xmlElement )
	if getStartsWithChainWord( word ):
		word = getValueByKeysXMLElement( word.split( '.' ), xmlElement )
		if word == None:
			return None
		if getIsXMLElement( word ):
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
		functionElement = xmlElement.getXMLElementByID( word )
		if functionElement != None:
			if functionElement.className == 'function':
				return EvaluatorFunction( word, functionElement )
		if nextWord == ':':
			return EvaluatorValue( word )
		return EvaluatorLocal( word, xmlElement )
	return EvaluatorNumeric( word, xmlElement )

def getValueByKeysXMLElement( keys, xmlElement ):
	"Get the value from the keys and xml element."
	for key in keys:
		xmlElement = xmlElement.getValueByKey( key )
	return xmlElement

def getStartsWithChainWord( word ):
	"Determine if the word starts with an element chain word."
	if word.startswith( 'vertex' ):
		return True
	dotIndex = word.find( '.' )
	if dotIndex < 0:
		return False
	return word[ : dotIndex ] in globalElementValueDictionary

def getIsXMLElement( value ):
	"Determine if the value is an xmlelement."
	return value.__class__.__name__ == 'XMLElement'

def addPrefixDictionary( dictionary, keys, prefix, value ):
	"Add prefixed key values to dictionary."
	for key in keys:
		dictionary[ prefix + key ] = value

def addSpacedPortionDirection( portionDirection, spacedPortionDirections ):
	"Add spaced portion directions."
	lastSpacedPortionDirection = spacedPortionDirections[ - 1 ]
	if portionDirection.portion - lastSpacedPortionDirection.portion > 0.003:
		spacedPortionDirections.append( portionDirection )
		return
	if portionDirection.directionReversed > lastSpacedPortionDirection.directionReversed:
		spacedPortionDirections.append( portionDirection )

def addToPathsRecursively( paths, vector3Lists ):
	"Add to vector3 paths recursively."
	if vector3Lists.__class__ == Vector3:
		paths.append( [ vector3Lists ] )
		return
	path = []
	for vector3List in vector3Lists:
		if vector3List.__class__ == list:
			addToPathsRecursively( paths, vector3List )
		elif vector3List.__class__ == Vector3:
			path.append( vector3List )
	if len( path ) > 0:
		paths.append( path )

def alterVerticesByEquation( vertices, xmlElement ):
	"Alter vertices by an equation."
	if 'equation' in xmlElement.attributeDictionary:
		equationResult = EquationResult( 'equation', xmlElement )
		for vertex in vertices:
			returnValue = equationResult.getReturnValue( vertex )
			if returnValue == None:
				print( 'Warning, returnValue in alterVerticesByEquation in evaluate is None for:' )
				print( xmlElement )
			else:
				getVector3ByFloatList( vertex, returnValue )
		equationResult.function.reset()
#later do xyz

def comparePortionDirection( portionDirection, otherPortionDirection ):
	"Comparison in order to sort portion directions in ascending order of portion then direction."
	if portionDirection.portion > otherPortionDirection.portion:
		return 1
	if portionDirection.portion < otherPortionDirection.portion:
		return - 1
	if portionDirection.directionReversed < otherPortionDirection.directionReversed:
		return - 1
	return portionDirection.directionReversed > otherPortionDirection.directionReversed

def convertToFloatList( dictionary ):
	'Recursively convert any Vector3 values to float lists.'
	for key in getKeys( dictionary ):
		value = dictionary[ key ]
		if value.__class__ == Vector3:
			dictionary[ key ] = value.getFloatList()
		else:
			convertToFloatList( dictionary[ key ] )

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
		if evaluatorWord in [ '(', '[', '{' ]:
			bracketBeginIndex = bracketEndIndex
		elif evaluatorWord in [ ')', ']', '}' ]:
			if bracketBeginIndex == None:
				print( 'Warning, bracketBeginIndex in evaluateBrackets in evaluate is None.' )
				print( 'This may be because the brackets are not balanced.' )
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

def getCommaSeparatedValues( value ):
	"Get comma separated values."
	commaSeparatedValues = []
	commaSeparatedValue = ''
	bracketLevel = 0
	for character in value:
		if character == '(' or character == '[' or character == '{':
			bracketLevel += 1
		if character == ')' or character == ']' or character == '}':
			bracketLevel -= 1
		if character == ',' and bracketLevel == 0:
			if len( commaSeparatedValue ) > 1:
				commaSeparatedValues.append( commaSeparatedValue )
			commaSeparatedValue = ''
		else:
			commaSeparatedValue += character
	if len( commaSeparatedValue ) > 1:
		commaSeparatedValues.append( commaSeparatedValue )
	return commaSeparatedValues

def getCreationDirectoryPath():
	"Get the creation directory path."
	return os.path.join( getShapesDirectoryPath(), 'creation' )

def getDictionarySplitWords( dictionary, value ):
	"Get split line for evaluators."
	for dictionaryKey in dictionary.keys():
		value = value.replace( dictionaryKey, ' ' + dictionaryKey + ' ' )
	dictionarySplitWords = []
	for word in value.split():
		dictionarySplitWords.append( word )
	return dictionarySplitWords

def getElementByElement( xmlElement ):
	"Get the xmlElement."
	return xmlElement

def getElementIDByElement( xmlElement ):
	"Get the xmlElement."
	return ElementID( xmlElement )

def getElementNameByElement( xmlElement ):
	"Get the xmlElement."
	return ElementName( xmlElement )

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
				print( 'Warning, getEvaluatedDictionary in evaluate can not get a value for:' )
				print( valueString )
				evaluatedDictionary[ key + '__Warning__' ] = 'Can not evaluate: ' + valueString.replace( '"', ' ' ).replace( "'", ' ' )
			else:
				evaluatedDictionary[ key ] = value
	return evaluatedDictionary

def getEvaluatedExpressionValue( value, xmlElement ):
	"Evaluate the expression value."
	try:
		return getEvaluatedExpressionValueBySplitLine( getEvaluatorSplitWords( value ), xmlElement )
	except:
		print( 'Warning, in getEvaluatedExpressionValue in evaluate could not get a value for:' )
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
		return evaluatedExpressionValueEvaluators[ 0 ].value
	return None

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

def getEvaluatedExpressionValueEvaluators( evaluators ):
	"Evaluate the expression value from the numeric and operation evaluators."
	for negativeIndex in xrange( 1 - len( evaluators ), 0 ):
		evaluatorIndex = negativeIndex + len( evaluators )
		evaluators[ evaluatorIndex ].executeRightOperation( evaluators, evaluatorIndex )
	executeLeftOperations( evaluators, 200 )
	for operationLevel in [ 60, 40, 20, 15 ]:
		executePairOperations( evaluators, operationLevel )
	executeLeftOperations( evaluators, 13 )
	for operationLevel in [ 12, 10, 0 ]:
		executePairOperations( evaluators, operationLevel )
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
			print( 'Warning, could not evaluate the int.' )
			print( key )
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
	if gcodec.getStartsWithByList( word, [ 'creation.', 'math.' ] ):
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
	value = str( xmlElement.attributeDictionary[ key ] ).strip()
	if key == 'id':
		return value
	return getEvaluatedLinkValue( value, xmlElement )

def getEvaluatorSplitWords( value ):
	"Get split words for evaluators."
	if value.startswith( '=' ):
		value = value[ len( '=' ) : ]
	global globalDictionaryOperatorBegin
	beginSplitWords = getDictionarySplitWords( globalDictionaryOperatorBegin, value )
	global globalSplitDictionaryOperator
	evaluatorSplitWords = []
	for beginSplitWord in beginSplitWords:
		if beginSplitWord in globalDictionaryOperatorBegin:
			evaluatorSplitWords.append( beginSplitWord )
		else:
			evaluatorSplitWords += getDictionarySplitWords( globalSplitDictionaryOperator, beginSplitWord )
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
	bracketedString = bracketedString.strip().replace( '[', '' ).replace( ']', '' ).replace( '(', '' ).replace( ')', '' )
	if len( bracketedString ) < 1:
		return []
	splitLine = bracketedString.split( ',' )
	floatList = []
	for word in splitLine:
		evaluatedFloat = euclidean.getFloatFromValue( word )
		if evaluatedFloat != None:
			floatList.append( evaluatedFloat )
	return floatList

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
	dotIndex = floatString.find( '.' )
	if dotIndex < 0:
		return int( value )
	return int( round( float( floatString ) ) )

def getIsBracketed( word ):
	"Determine if the word is bracketed."
	if word == '':
		return False
	firstCharacter = word[ 0 ]
	lastCharacter = word[ - 1 ]
	if firstCharacter == '(' and lastCharacter == ')':
		return True
	return firstCharacter == '[' and lastCharacter == ']'

def getMatchingPlugins( namePathDictionary, xmlElement ):
	"Get the plugins whose names are in the attribute dictionary."
	matchingPlugins = []
	for key in xmlElement.attributeDictionary:
		if key in namePathDictionary:
			if euclidean.getBooleanFromValue( getEvaluatedValueObliviously( key, xmlElement ) ):
				pluginModule = gcodec.getModuleWithPath( namePathDictionary[ key ] )
				if pluginModule != None:
					matchingPlugins.append( pluginModule )
	return matchingPlugins

def getParentByElement( xmlElement ):
	"Get the parent."
	return xmlElement.parent

def getPathByKey( key, xmlElement ):
	"Get path from prefix and xml element."
	if key not in xmlElement.attributeDictionary:
		return []
	value = str( xmlElement.attributeDictionary[ key ] ).strip()
	if getStartsWithCurlyEqualRoundSquare( value ):
		value = getEvaluatedExpressionValue( value, xmlElement )
		return getPathByList( value )
	pathElement = getXMLElementByValue( value, xmlElement )
	if pathElement == None:
		print( 'Warning, no path element in evaluate in getPathByKey.' )
		print( pathElement )
		return []
	return pathElement.object.getPaths()[ 0 ]

def getPathByList( vertexList ):
	"Get the paths by list."
	if len( vertexList ) < 1:
		return Vector3()
	if vertexList[ 0 ].__class__ != list:
		vertexList = [ vertexList ]
	path = []
	for floatList in vertexList:
		vector3 = getVector3ByFloatList( Vector3(), floatList )
		path.append( vector3 )
	return path

def getPathByPrefix( path, prefix, xmlElement ):
	"Get path from prefix and xml element."
	if len( path ) < 2:
		print( 'Warning, bug, path is too small in evaluate in setPathByPrefix.' )
		return
	pathByKey = getPathByKey( prefix + 'path', xmlElement )
	if len( pathByKey ) < len( path ):
		for pointIndex in xrange( len( pathByKey ) ):
			path[ pointIndex ] = pathByKey[ pointIndex ]
	else:
		path = pathByKey
	path[ 0 ] = getVector3ByPrefix( prefix + 'from', path[ 0 ], xmlElement )
	path[ - 1 ] = getVector3ByPrefix( prefix + 'to', path[ - 1 ], xmlElement )
	return path

def getPathsByKey( key, xmlElement ):
	"Get paths by key."
	if key not in xmlElement.attributeDictionary:
		return []
	value = str( xmlElement.attributeDictionary[ key ] ).strip()
	paths = getPathsByValue( value, xmlElement )
	if len( paths ) > 0:
		return paths
	commaSeparatedValues = getCommaSeparatedValues( value )
	for commaSeparatedValue in commaSeparatedValues:
		paths += getPathsByValue( commaSeparatedValue.strip(), xmlElement )
	return paths

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

def getPathsByValue( value, xmlElement ):
	"Get paths by value."
	if getStartsWithCurlyEqualRoundSquare( value ):
		value = getEvaluatedExpressionValue( value, xmlElement )
		return getPathsByLists( value )
	pathElement = getXMLElementByValue( value, xmlElement )
	if pathElement == None:
		return []
	if pathElement.object == None:
		return []
	return pathElement.object.getPaths()

def getPrecision( xmlElement ):
	"Get the cascade precision."
	if xmlElement == None:
		return 0.1
	return xmlElement.getCascadeFloat( 0.1, 'precision' )

def getRootByElement( xmlElement ):
	"Get the root."
	return xmlElement.getRoot()

def getSides( radius, xmlElement ):
	"Get the nunber of poygon sides."
	return math.sqrt( 0.5 * radius * math.pi * math.pi / getPrecision( xmlElement ) )

def getShapesDirectoryPath():
	"Get the solids directory path."
	return settings.getPathInFabmetheus( os.path.join( 'fabmetheus_utilities', 'shapes' ) )

def getSpacedPortionDirections( interpolationDictionary ):
	"Get sorted portion directions."
	portionDirections = []
	for interpolationDictionaryValue in interpolationDictionary.values():
		portionDirections += interpolationDictionaryValue.portionDirections
	portionDirections.sort( comparePortionDirection )
	if len( portionDirections ) < 1:
		return []
	spacedPortionDirections = [ portionDirections[ 0 ] ]
	for portionDirection in portionDirections[ 1 : ]:
		addSpacedPortionDirection( portionDirection, spacedPortionDirections )
	return spacedPortionDirections

def getSplitDictionary():
	"Get split dictionary."
	global globalSplitDictionaryOperator
	splitDictionary = globalSplitDictionaryOperator.copy()
	global globalDictionaryOperatorBegin
	splitDictionary.update( globalDictionaryOperatorBegin )
	addPrefixDictionary( splitDictionary, globalMathConstantDictionary.keys(), 'math.', EvaluatorConstant )
	splitDictionary[ 'and' ] = EvaluatorAnd
	splitDictionary[ 'false' ] = EvaluatorFalse
	splitDictionary[ 'False' ] = EvaluatorFalse
	splitDictionary[ 'or' ] = EvaluatorOr
	splitDictionary[ 'not' ] = EvaluatorNot
	splitDictionary[ 'true' ] = EvaluatorTrue
	splitDictionary[ 'True' ] = EvaluatorTrue
	pluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( getCreationDirectoryPath() )
	addPrefixDictionary( splitDictionary, pluginFileNames, 'math.', EvaluatorCreation )
	functionNameString = 'acos asin atan atan2 ceil cos cosh degrees exp fabs floor fmod frexp hypot ldexp log log10 modf pow radians sin sinh sqrt tan tanh'
	addPrefixDictionary( splitDictionary, functionNameString.split(), 'math.', EvaluatorMath )
	return splitDictionary

def getStartsWithCurlyEqualRoundSquare( word ):
	"Determine if the word starts with round or square brackets."
	return word.startswith( '{' ) or word.startswith( '=' ) or word.startswith( '(' ) or word.startswith( '[' )

def getTypeLength( value ):
	"Get the type length of the value."
	if value == None or value == '':
		return 0
	valueString = str( value )
	if valueString.startswith( '{' ) or valueString.startswith( '(' ) or valueString.startswith( '[' ):
		return len( getKeys( value ) )
	if euclidean.getFloatFromValue( value ) == None:
		return 0
	return - 1

def getVector3ByFloatList( vector3, floatList ):
	"Get vector3 by float list."
	if len( floatList ) > 0:
		vector3.x = euclidean.getFloatFromValue( floatList[ 0 ] )
	if len( floatList ) > 1:
		vector3.y = euclidean.getFloatFromValue( floatList[ 1 ] )
	if len( floatList ) > 2:
		vector3.z = euclidean.getFloatFromValue( floatList[ 2 ] )
	return vector3

def getVector3ByKey( key, vector3, xmlElement ):
	"Get vector3 by key and xml element."
	value = getEvaluatedValue( key, xmlElement )
	if value == None:
		return vector3
	vector3String = str( value ).strip()
	floatList = getFloatListFromBracketedString( vector3String )
	if floatList == None:
		if getTypeLength( value ) == - 1:
			floatValue = float( value )
			return Vector3( floatValue, floatValue, floatValue )
		return vector3
	return getVector3ByFloatList( getVector3IfNone( vector3 ), floatList )

def getVector3ByPrefix( prefix, vector3, xmlElement ):
	"Get vector3 from prefix and xml element."
	vector3 = getVector3ByKey( prefix, vector3, xmlElement )
	x = getEvaluatedFloat( prefix + 'x', xmlElement )
	if x != None:
		vector3 = getVector3IfNone( vector3 )
		vector3.x = x
	y = getEvaluatedFloat( prefix + 'y', xmlElement )
	if y != None:
		vector3 = getVector3IfNone( vector3 )
		vector3.y = y
	z = getEvaluatedFloat( prefix + 'z', xmlElement )
	if z != None:
		vector3 = getVector3IfNone( vector3 )
		vector3.z = z
	return vector3

def getVector3FromXMLElement( xmlElement ):
	"Get vector3 from xml element."
	return Vector3( getEvaluatedFloatZero( 'x', xmlElement ), getEvaluatedFloatZero( 'y', xmlElement ), getEvaluatedFloatZero( 'z', xmlElement ) )

def getVector3IfNone( vector3 ):
	"Get new vector3 if the original vector3 is none."
	if vector3 == None:
		return Vector3()
	return vector3

def getVector3ListsRecursively( floatLists ):
	"Get vector3 lists recursively."
	if len( floatLists ) < 1:
		return Vector3()
	firstElement = floatLists[ 0 ]
	if firstElement.__class__ != list:
		return getVector3ByFloatList( Vector3(), floatLists )
	vector3ListsRecursively = []
	for floatList in floatLists:
		vector3ListsRecursively.append( getVector3ListsRecursively( floatList ) )
	return vector3ListsRecursively

def getVector3ThroughSizeDiameter( vector3, xmlElement ):
	"Get vector3 from prefix and xml element."
	vector3 = getVector3ByPrefix( 'size', vector3, xmlElement )
	return 0.5 * getVector3ByPrefix( 'diameter', vector3 + vector3, xmlElement )

def getVertexByElement( xmlElement ):
	"Get the vertex list."
	vertexElements = xmlElement.getChildrenWithClassName( 'vertex' )
	path = []
	for vertexElement in vertexElements:
		path.append( getVector3FromXMLElement( vertexElement ).getFloatList() )
	return path

def getVerticesByKey( key, xmlElement ):
	"Get the vertices by key."
	verticesElement = getXMLElementByKey( key, xmlElement )
	if verticesElement == None:
		return []
	if verticesElement.object == None:
		return []
	return verticesElement.object.getVertices()

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

def getXMLElementByKey( key, xmlElement ):
	"Get the xml element by key."
	if key not in xmlElement.attributeDictionary:
		return None
	value = str( xmlElement.attributeDictionary[ key ] ).strip()
	return getXMLElementByValue( value, xmlElement )

def getXMLElementByValue( value, xmlElement ):
	"Get the xml element by value."
	if value.startswith( 'id.' ):
		return xmlElement.getXMLElementByImportID( value[ len( 'id.' ) : ] )
	if value.startswith( 'name.' ):
		return xmlElement.getXMLElementByImportName( value[ len( 'name.' ) : ] )
	if value.startswith( 'parent.' ):
		return xmlElement.parent
	return xmlElement.getXMLElementByImportName( value )

def processArchivable( archivableClass, xmlElement, xmlProcessor ):
	"Get any new elements and process the archivable."
	if xmlElement == None:
		return
	getArchivableObject( archivableClass, xmlElement )
	xmlProcessor.processChildren( xmlElement )


class ElementID:
	"A class to get an element by ID."
	def __init__( self, xmlElement ):
		"Initialize."
		self.xmlElement = xmlElement

	def getValueByKey( self, key ):
		"Get value by the key."
		return self.xmlElement.getXMLElementByID( key )


class ElementName:
	"A class to get an element by name."
	def __init__( self, xmlElement ):
		"Initialize."
		self.xmlElement = xmlElement

	def getValueByKey( self, key ):
		"Get value by the key."
		return self.xmlElement.getXMLElementByName( key )


class Evaluator:
	'Base evaluator class.'
	def __init__( self, word, xmlElement ):
		'Set value to none.'
		self.value = None
		self.word = word

	def __repr__( self ):
		"Get the string representation of this Evaluator."
		return '%s: %s, %s' % ( self.__class__.__name__, self.word, self.value )

	def executeBracket( self, bracketBeginIndex, bracketEndIndex, evaluators ):
		'Execute the bracket.'
		pass

	def executeFunction( self, evaluators, evaluatorIndex, nextEvaluator ):
		'Execute the function.'
		pass

	def executeKey( self, evaluators, key, evaluatorIndex, nextEvaluator ):
		'Execute the key index.'
		if self.value.__class__ == list:
			del evaluators[ evaluatorIndex ]
			arrayIndexFloat = euclidean.getFloatFromValue( key )
			if arrayIndexFloat == None:
				nextEvaluator.value = None
				return
			keyIndex = int( round( arrayIndexFloat ) )
			if keyIndex >= 0 and keyIndex < len( self.value ):
				nextEvaluator.value = self.value[ keyIndex ]
			else:
				nextEvaluator.value = None
				print( 'Warning, keyIndex in executeKey in Evaluator in evaluate is out of range for:' )
				print( keyIndex )
				print( self.value )
			return
		if self.value.__class__ == dict:
			del evaluators[ evaluatorIndex ]
			if key in self.value:
				nextEvaluator.value = self.value[ key ]
			else:
				nextEvaluator.value = None
				print( 'Warning, key in executeKey in Evaluator in evaluate is not in for:' )
				print( key )
				print( self.value )

	def executeLeftOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Execute operator which acts from the left.'
		pass

	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		pass

	def executeRightOperation( self, evaluators, evaluatorIndex ):
		'Execute operator which acts from the right.'
		pass


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
			return self.getValueFromValuePair( euclidean.getFloatFromValue( leftValue ), euclidean.getFloatFromValue( rightValue ) )
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
			print( 'Warning, can not minus.' )
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
		evaluatedExpressionValueEvaluators = getBracketEvaluators( bracketBeginIndex, bracketEndIndex, evaluators )
		self.value = {}
		for evaluatedExpressionValueEvaluator in evaluatedExpressionValueEvaluators:
			keyValue = evaluatedExpressionValueEvaluator.value
			self.value[ keyValue.key ] = keyValue.value
		del evaluators[ bracketBeginIndex + 1: bracketEndIndex + 1 ]


class EvaluatorBracketRound( Evaluator ):
	'Class to evaluate a string.'
	def __init__( self, word, xmlElement ):
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
			self.value = self.arguments[ 0 ]

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
		if len( self.value ) != 1:
			return
		evaluators[ previousIndex ].executeKey( evaluators, self.value[ 0 ], previousIndex, self )


class EvaluatorComma( Evaluator ):
	'Class to join two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 0:
			del evaluators[ evaluatorIndex ]


class EvaluatorConstant( Evaluator ):
	'Class to evaluate a string.'
	def __init__( self, word, xmlElement ):
		'Set value.'
		self.word = word
		global globalMathConstantDictionary
		self.value = globalMathConstantDictionary[ word[ len( 'math.' ) : ] ]


class EvaluatorCreation( Evaluator ):
	'Creation evaluator class.'
	def __init__( self, word, xmlElement ):
		'Set value to none.'
		self.value = None
		self.word = word
		self.xmlElement = xmlElement

	def executeFunction( self, evaluators, evaluatorIndex, nextEvaluator ):
		'Execute the function.'
		pluginModule = gcodec.getModuleWithPath( os.path.join( getCreationDirectoryPath(), self.getFunctionName() ) )
		if pluginModule == None:
			print( 'Warning, the EvaluatorCreation in evaluate can not get a pluginModule for:' )
			print( self.getFunctionName() )
			print( self )
			return
		dictionary = {}
		firstArgument = None
		if len( nextEvaluator.arguments ) > 0:
			firstArgument = nextEvaluator.arguments[ 0 ]
		if firstArgument.__class__ == dict:
			dictionary = firstArgument
		else:
			dictionary[ '_arguments' ] = nextEvaluator.arguments
		dictionary[ '_fromEvaluatorCreation' ] = 'true'
		nextEvaluator.value = pluginModule.getGeometryOutput( self.xmlElement.getShallowCopy( dictionary ) )
		convertToFloatList( nextEvaluator.value )
		del evaluators[ evaluatorIndex ]

	def getFunctionName( self ):
		'Get the function name.'
		return self.word[ len( 'math.' ) : ].lower()


class EvaluatorDictionary( Evaluator ):
	'Class to join two evaluators.'
	def executePairOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel != 10:
			return
		leftEvaluator = evaluators[ evaluatorIndex - 1 ]
		leftValue = leftEvaluator.value
		rightIndex = evaluatorIndex + 1
		if rightIndex >= len( evaluators ):
			leftEvaluator.value = KeyValue( leftValue, None )
			del evaluators[ evaluatorIndex ]
			return
		rightEvaluator = evaluators[ rightIndex ]
		if rightEvaluator.__class__ == EvaluatorComma:
			leftEvaluator.value = KeyValue( leftValue, None )
			del evaluators[ evaluatorIndex ]
			return
		rightValue = rightEvaluator.value
		leftEvaluator.value = KeyValue( leftValue, rightValue )
		del evaluators[ evaluatorIndex : evaluatorIndex + 2 ]


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
	def __init__( self, word, xmlElement ):
		'Set value to zero.'
		self.value = 0
		self.word = word


class EvaluatorFunction( EvaluatorCreation ):
	'Function evaluator class.'
	def executeFunction( self, evaluators, evaluatorIndex, nextEvaluator ):
		'Execute the function.'
		if self.xmlElement.object == None:
			if 'return' in self.xmlElement.attributeDictionary:
				value = self.xmlElement.attributeDictionary[ 'return' ]
				self.xmlElement.object = getEvaluatorSplitWords( value )
			else:
				self.xmlElement.object = []
		self.function = Function( self.xmlElement.object, self.xmlElement )
		self.setFunctionLocalTable( nextEvaluator )
		nextEvaluator.value = self.function.getReturnValue()
		del evaluators[ evaluatorIndex ]

	def setFunctionLocalTable( self, nextEvaluator ):
		'Evaluate the function statement and delete the evaluators.'
		self.function.localTable[ '_arguments' ] = nextEvaluator.arguments
		if len( nextEvaluator.arguments ) > 0:
			firstArgument = nextEvaluator.arguments[ 0 ]
			if firstArgument.__class__ == dict:
				self.function.localTable = firstArgument
				return
		if 'parameters' not in self.function.xmlElement.attributeDictionary:
			return
		parameters = self.function.xmlElement.attributeDictionary[ 'parameters' ].strip()
		if parameters == '':
			return
		parameterWords = parameters.split( ',' )
		for parameterWordIndex, parameterWord in enumerate( parameterWords ):
			strippedWord = parameterWord.strip()
			keyValue = KeyValue().getByEqual( strippedWord )
			if parameterWordIndex < len( nextEvaluator.arguments ):
				self.function.localTable[ keyValue.key ] = nextEvaluator.arguments[ parameterWordIndex ]
			else:
				strippedValue = keyValue.value
				if strippedValue == None:
					print( 'Warning there is no default parameter in getParameterValue for:' )
					print( strippedWord )
					print( parameterWords )
					print( nextEvaluator.arguments )
					print( self.function.xmlElement.attributeDictionary )
				else:
					strippedValue = strippedValue.strip()
				self.function.localTable[ keyValue.key.strip() ] = strippedValue
		if len( nextEvaluator.arguments ) > len( parameterWords ):
			print( 'Warning there are too many function parameters for:' )
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
	def __init__( self, word, xmlElement ):
		'Set value.'
		self.word = word
		self.value = None
		functions = xmlElement.getRoot().xmlProcessor.functions
		if len( functions ) < 1:
			return
		localTable = functions[ - 1 ].localTable
		if word in localTable:
			self.value = localTable[ word ]


class EvaluatorMath( EvaluatorCreation ):
	'Math evaluator class.'
	def executeFunction( self, evaluators, evaluatorIndex, nextEvaluator ):
		'Execute the function.'
		function = math.__dict__[ self.getFunctionName() ]
		argumentsCopy = nextEvaluator.arguments[ : ]
		if len( argumentsCopy ) == 1:
			firstElement = argumentsCopy[ 0 ]
			if firstElement.__class__ == list:
				argumentsCopy = firstElement
		while len( argumentsCopy ) > 0:
			try:
				result = function( *argumentsCopy )
				nextEvaluator.value = result
				del evaluators[ evaluatorIndex ]
				return
			except:
				argumentsCopy = argumentsCopy[ : - 1 ]
		print( 'Warning, the EvaluatorMath in evaluate can not handle:' )
		print( self )
		print( nextEvaluator.arguments )
		print( nextEvaluator )
		del evaluators[ evaluatorIndex ]


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
	def __init__( self, word, xmlElement ):
		'Set value.'
		self.word = word
		self.value = getFloatIfFloat( word )


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
		return math.pow( leftValue, rightValue )


class EvaluatorTrue( Evaluator ):
	'Class to evaluate a string.'
	def __init__( self, word, xmlElement ):
		'Set value to one.'
		self.value = 1
		self.word = word


class EvaluatorValue( Evaluator ):
	'Class to evaluate a string.'
	def __init__( self, word ):
		'Set value to none.'
		self.value = word
		self.word = str( word )


class EquationResult:
	"Class to get equation results."
	def __init__( self, key, xmlElement ):
		"Initialize."
		self.function = Function( getEvaluatorSplitWords( xmlElement.attributeDictionary[ key ] ), xmlElement )

	def getReturnValue( self, vertex ):
		"Get return value."
		if self.function == None:
			return vertex
		self.function.localTable[ 'x' ] = vertex.x
		self.function.localTable[ 'y' ] = vertex.y
		self.function.localTable[ 'z' ] = vertex.z
		return self.function.getReturnValueWithoutDeletion()


class Function:
	"Class to get equation results."
	def __init__( self, evaluatorSplitLine, xmlElement ):
		"Initialize."
		self.evaluatorSplitLine = evaluatorSplitLine
		self.localTable = {}
		self.returnValue = None
		self.xmlElement = xmlElement
		self.xmlProcessor = xmlElement.getRoot().xmlProcessor
		self.xmlProcessor.functions.append( self )

	def __repr__( self ):
		"Get the string representation of this Function."
		return '%s, %s, %s' % ( self.evaluatorSplitLine, self.localTable, self.returnValue )

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
		del self.xmlElement.getRoot().xmlProcessor.functions[ - 1 ]


class Interpolation:
	"Class to interpolate a path."
	def __init__( self ):
		"Set index."
		self.interpolationIndex = 0

	def getByDistances( self ):
		"Get by distances."
		beginDistance = self.distances[ 0 ]
		self.interpolationLength = self.distances[ - 1 ] - beginDistance
		self.close = abs( 0.000001 * self.interpolationLength )
		self.portionDirections = []
		oldDistance = beginDistance - self.interpolationLength
		for distance in self.distances:
			portionDirection = PortionDirection( distance / self.interpolationLength )
			if abs( distance - oldDistance ) < self.close:
				portionDirection.directionReversed = True
			self.portionDirections.append( portionDirection )
			oldDistance = distance
		return self

	def getByPrefixAlong( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element along the path."
		if len( path ) < 2:
			print( 'Warning, path is too small in evaluate in Interpolation.' )
			return
		self.path = getPathByPrefix( path, prefix, xmlElement )
		self.distances = [ 0.0 ]
		previousPoint = self.path[ 0 ]
		for point in self.path[ 1 : ]:
			distanceDifference = abs( point - previousPoint )
			self.distances.append( self.distances[ - 1 ] + distanceDifference )
			previousPoint = point
		return self.getByDistances()

	def getByPrefixX( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element in the z direction."
		if len( path ) < 2:
			print( 'Warning, path is too small in evaluate in Interpolation.' )
			return
		self.path = getPathByPrefix( path, prefix, xmlElement )
		self.distances = []
		for point in self.path:
			self.distances.append( point.x )
		return self.getByDistances()

	def getByPrefixZ( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element in the z direction."
		if len( path ) < 2:
			print( 'Warning, path is too small in evaluate in Interpolation.' )
			return
		self.path = getPathByPrefix( path, prefix, xmlElement )
		self.distances = []
		for point in self.path:
			self.distances.append( point.z )
		return self.getByDistances()

	def getComparison( self, first, second ):
		"Compare the first with the second."
		if abs( second - first ) < self.close:
			return 0
		if second > first:
			return 1
		return - 1

	def getComplexByPortion( self, portionDirection ):
		"Get complex from z portion."
		self.setInterpolationIndexFromTo( portionDirection )
		return self.oneMinusInnerPortion * self.fromVertex.dropAxis( 2 ) + self.innerPortion * self.toVertex.dropAxis( 2 )

	def getInnerPortion( self ):
		"Get inner x portion."
		fromDistance = self.distances[ self.interpolationIndex ]
		innerLength = self.distances[ self.interpolationIndex + 1 ] - fromDistance
		if abs( innerLength ) == 0.0:
			return 0.0
		return ( self.absolutePortion - fromDistance ) / innerLength

	def getVector3ByPortion( self, portionDirection ):
		"Get vector3 from z portion."
		self.setInterpolationIndexFromTo( portionDirection )
		return self.oneMinusInnerPortion * self.fromVertex + self.innerPortion * self.toVertex

	def getYByPortion( self, portionDirection ):
		"Get y from x portion."
		self.setInterpolationIndexFromTo( portionDirection )
		return self.oneMinusInnerPortion * self.fromVertex.y + self.innerPortion * self.toVertex.y

	def setInterpolationIndex( self, portionDirection ):
		"Set the interpolation index."
		self.absolutePortion = self.distances[ 0 ] + self.interpolationLength * portionDirection.portion
		interpolationIndexes = range( 0, len( self.distances ) - 1 )
		if portionDirection.directionReversed:
			interpolationIndexes.reverse()
		for self.interpolationIndex in interpolationIndexes:
			begin = self.distances[ self.interpolationIndex ]
			end = self.distances[ self.interpolationIndex + 1 ]
			if self.getComparison( begin, self.absolutePortion ) != self.getComparison( end, self.absolutePortion ):
				return

	def setInterpolationIndexFromTo( self, portionDirection ):
		"Set the interpolation index, the from vertex and the to vertex."
		self.setInterpolationIndex( portionDirection )
		self.innerPortion = self.getInnerPortion()
		self.oneMinusInnerPortion = 1.0 - self.innerPortion
		self.fromVertex = self.path[ self.interpolationIndex ]
		self.toVertex = self.path[ self.interpolationIndex + 1 ]


class KeyValue:
	"Class to hold a key value."
	def __init__( self, key = None, value = None ):
		"Get key value."
		self.key = key
		self.value = value

	def __repr__( self ):
		"Get the string representation of this KeyValue."
		return '%s : %s' % ( self.key, self.value )

	def getByCharacter( self, character, line ):
		"Get by character."
		dotIndex = line.find( character )
		if dotIndex < 0:
			self.key = line
			return self
		self.key = line[ : dotIndex ]
		self.value = line[ dotIndex + 1 : ]
		return self

	def getByDot( self, line ):
		"Get by dot."
		return self.getByCharacter( '.', line )

	def getByEqual( self, line ):
		"Get by dot."
		return self.getByCharacter( '=', line )


class PortionDirection:
	"Class to hold a portion and direction."
	def __init__( self, portion ):
		"Initialize."
		self.directionReversed = False
		self.portion = portion

	def __repr__( self ):
		"Get the string representation of this PortionDirection."
		return '%s: %s' % ( self.portion, self.directionReversed )


class RadiusXY:
	'Class to get a radius.'
	def __repr__( self ):
		"Get the string representation of this RadiusXY."
		return '%s, %s, %s' % ( self.radius, self.radiusX, self.radiusY )

	def getByRadius( self, radius, xmlElement ):
		'Get by radius.'
		self.radius = radius
		self.radiusX = getEvaluatedFloatDefault( self.radius, 'radiusx', xmlElement )
		self.radiusY = getEvaluatedFloatDefault( self.radius, 'radiusy', xmlElement )
		if self.radiusX != radius or self.radiusY != radius:
			self.radius = math.sqrt( self.radiusX * self.radiusY )
		return self

	def getByXMLElement( self, xmlElement ):
		'Get by xmlElement.'
		return self.getByRadius( getEvaluatedFloatDefault( 1.0, 'radius', xmlElement ), xmlElement )


globalDictionaryOperatorBegin = {
	'==' : EvaluatorEqual,
	'>=' : EvaluatorGreaterEqual,
	'<=' : EvaluatorLessEqual,
	'!=' : EvaluatorNotEqual,
	'**' : EvaluatorPower }

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
	'*' : EvaluatorMultiplication,
	'-' : EvaluatorSubtraction }

#Constants from: http://www.physlink.com/reference/MathConstants.cfm
globalMathConstantDictionary = {
	'e' : math.e,
	'euler' : 0.5772156649015328606065120,
	'golden' : 1.6180339887498948482045868,
	'pi' : math.pi }
#If anyone wants to add stuff, more constants are at: http://en.wikipedia.org/wiki/Mathematical_constant
globalSplitDictionary = getSplitDictionary()

globalElementValueDictionary = {
	'element' : getElementByElement,
	'id' : getElementIDByElement,
	'name' : getElementNameByElement,
	'parent' : getParentByElement,
	'root' : getRootByElement,
	'vertex' : getVertexByElement }
