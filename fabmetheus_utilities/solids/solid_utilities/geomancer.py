"""
Boolean geometry utilities.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
from fabmetheus_utilities import xml_simple_parser
import math
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def addEvaluator( evaluators, splitDictionary, word, xmlElement ):
	"Get the evaluator."
	word = word.strip()
	if word == '':
		return
	if word in splitDictionary:
		evaluators.append( splitDictionary[ word ]( word, xmlElement ) )
		return 
	evaluators.append( NumericEvaluator( word, xmlElement ) )

def addKeys( fromKeys, toKeys ):
	'Add keys from the list to the list.'
	if fromKeys == None:
		return
	for fromKey in fromKeys:
		if fromKey not in toKeys:
			toKeys.append( fromKey )

def evaluateBrackets( evaluators, evaluatorIndex, evaluatorWord, lastBracketIndex ):
	"Evaluate the expression value from within the brackets."
	subEvaluators = evaluators[ evaluatorIndex + 1 : lastBracketIndex ]
	subEvaluatorsCopy = subEvaluators[ : ]
	withinEvaluators = getEvaluatedExpressionValueEvaluators( subEvaluators )
	if evaluatorWord == '[':
		if len( subEvaluators ) == 0:
			withinEvaluator = evaluators[ evaluatorIndex ]
			withinEvaluator.value = []
			withinEvaluator.word = '[]'
			withinEvaluators = [ withinEvaluator ]
		elif not getHasListEvaluator( subEvaluatorsCopy ):
			withinEvaluators[ 0 ].convertValueToList()
	if lastBracketIndex == None:
		print( 'Warning, lastBracketIndex in evaluateBrackets in geomancer is None.' )
		print( 'This may be because the brackets are not balanced.' )
		print( evaluators )
		return
	for deletionIndex in xrange( lastBracketIndex, evaluatorIndex + len( withinEvaluators ) - 1, - 1 ):
		del evaluators[ deletionIndex ]
	for overwriteIndex in xrange( len( withinEvaluators ) ):
		evaluators[ overwriteIndex + evaluatorIndex ] = withinEvaluators[ overwriteIndex ]
	previousIndex = evaluatorIndex - 1
	if previousIndex >= 0:
		 evaluators[ previousIndex ].executeMath( evaluators, evaluatorIndex, withinEvaluators )

def evaluateOperationLevel( evaluators, operationLevel ):
	"Evaluate the evaluators with the given operation level."
	for evaluatorIndex in xrange( len( evaluators ) - 1, 0, - 1 ):
		evaluator = evaluators[ evaluatorIndex ]
		evaluator.executeOperation( evaluators, evaluatorIndex, operationLevel )

def getArchivableObject( archivableClass, xmlElement ):
	"Get the archivable object."
	archivableObject = archivableClass()
	archivableObject.xmlElement = xmlElement
	xmlElement.object = archivableObject
	archivableObject.setToObjectAttributeDictionary()
	xmlElement.parent.object.archivableObjects.append( archivableObject )
	return archivableObject

def getBracketsExist( evaluators ):
	"Evaluate the expression value."
	lastBracketIndex = None
	for evaluatorIndex in xrange( len( evaluators ) - 1, - 1, - 1 ):
		evaluatorWord = evaluators[ evaluatorIndex ].word
		if evaluatorWord == ')' or evaluatorWord == ']':
			lastBracketIndex = evaluatorIndex
		elif evaluatorWord == '(' or evaluatorWord == '[':
			evaluateBrackets( evaluators, evaluatorIndex, evaluatorWord, lastBracketIndex )
			return True
	return False

def getCreatorsDirectoryPath():
	"Get the creators directory path."
	return os.path.join( getSolidsDirectoryPath(), 'creators' )

def getEvaluatedDictionary( evaluationKeys, xmlElement ):
	"Get the evaluated dictionary."
	evaluatedDictionary = {}
	zeroLength = ( len( evaluationKeys ) == 0 )
	for key in xmlElement.attributeDictionary.keys():
		if key in evaluationKeys or zeroLength:
			value = getEvaluatedValueWithoutChecking( key, xmlElement )
			if value == '' or value == None:
				valueString = str(xmlElement.attributeDictionary[ key ]  )
				print( 'Warning, %s does not evaluate.' % valueString )
				evaluatedDictionary[ '__Warning__' + valueString ] = 'Does not evaluate.'
			else:
				evaluatedDictionary[ key ] = value
	return evaluatedDictionary

def getEvaluatedExpressionValue( value, xmlElement ):
	"Evaluate the expression value."
	if value.startswith( '=' ):
		value = value[ len( '=' ) : ]
	powerToken = getUniqueToken( value, '__PoweR__' )
	splitToken = getUniqueToken( value, '__SpliT__' )
	value = value.replace( '**', powerToken ).replace( '{', '(' ).replace( '}', ')' )
	global globalSplitDictionary
	splitDictionary = globalSplitDictionary.copy()
	splitDictionary[ powerToken ] = PowerEvaluator
	splitDictionaryKeys = splitDictionary.keys()
	for splitDictionaryKey in splitDictionaryKeys:
		value = value.replace( splitDictionaryKey, splitToken + splitDictionaryKey + splitToken )
	splitLine = value.split( splitToken )
	evaluators = []
	for word in splitLine:
		addEvaluator( evaluators, splitDictionary, word, xmlElement )
	while getBracketsExist( evaluators ):
		pass
	evaluatedExpressionValueEvaluators = getEvaluatedExpressionValueEvaluators( evaluators )
	if len( evaluatedExpressionValueEvaluators ) > 0:
		return evaluatedExpressionValueEvaluators[ 0 ].value
	return None

def getEvaluatedExpressionValueEvaluators( evaluators ):
	"Evaluate the expression value from the numeric and operation evaluators."
	for evaluatorIndex in xrange( len( evaluators ) - 2, - 1, - 1 ):
		evaluators[ evaluatorIndex ].executeMinus( evaluators, evaluatorIndex )
	for operationLevel in [ 60, 40, 20, 10, 0 ]:
		evaluateOperationLevel( evaluators, operationLevel )
	return evaluators

def getEvaluatedFloat( key, xmlElement ):
	"Get the evaluated value as a float."
	if key in xmlElement.attributeDictionary:
		return getEvaluatedFloatFromValue( getEvaluatedValueWithoutChecking( key, xmlElement ) )
	return None

def getEvaluatedFloatDefault( defaultValue, key, xmlElement ):
	"Get the evaluated value as a float."
	evaluatedFloat = getEvaluatedFloat( key, xmlElement )
	if evaluatedFloat == None:
		return defaultValue
	return evaluatedFloat

def getEvaluatedFloatFromValue( value ):
	"Get the value as a float."
	try:
		return float( value )
	except:
		print( 'Warning, could not evaluate the float.' )
		print( value )
	return None

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
			return getIntFromFloatString( getEvaluatedValueWithoutChecking( key, xmlElement ) )
		except:
			print( 'Warning, could not evaluate the int.' )
			print( key )
			print( xmlElement.attributeDictionary[ key ] )
	return None

def getEvaluatedIntOne( key, xmlElement ):
	"Get the evaluated value as an int with a default of one."
	evaluatedInt = getEvaluatedInt( key, xmlElement )
	if evaluatedInt == None:
		return 1
	return evaluatedInt

def getEvaluatedIDValue( value, xmlElement ):
	"Evaluate the id value."
	keyValue = KeyValue( value[ len( 'id.' ) : ] )
	if keyValue.value == None:
		return value
	idElement = xmlElement.getXMLElementByID( keyValue.key )
	return getEvaluatedLinkValueByLookingInDictionary( keyValue.value, idElement )

def getEvaluatedLinkValue( value, xmlElement ):
	"Get the evaluated link value."
	if value.startswith( 'id.' ):
		return getEvaluatedIDValue( value, xmlElement )
	if value.startswith( 'math.' ):
		return getEvaluatedMathValue( value, xmlElement )
	if value.startswith( 'name.' ):
		return getEvaluatedNameValue( value, xmlElement )
	if value.startswith( 'parent.' ):
		return getEvaluatedParentValue( value, xmlElement )
	if value.startswith( 'root.' ):
		return getEvaluatedRootValue( value, xmlElement )
	if value.startswith( 'self.' ):
		return getEvaluatedSelfValue( value, xmlElement )
	if value.startswith( 'vertex.' ):
		return getEvaluatedVertexValue( value, xmlElement )
	if getStartsWithCurlyEqualRoundSquare( value ):
		return getEvaluatedExpressionValue( value, xmlElement )
	return value

def getEvaluatedLinkValueByLookingInDictionary( value, xmlElement ):
	"Evaluate the parent value."
	if value in xmlElement.attributeDictionary:
		value = str( xmlElement.attributeDictionary[ value ] )
	return getEvaluatedLinkValue( value.lstrip(), xmlElement )

def getEvaluatedMathValue( value, xmlElement ):
	"Evaluate the math value."
	value = value[ len( 'math.' ) : ]
	mathConstantDictionary = { 'e' : math.e, 'pi' : math.pi }
	if value in mathConstantDictionary:
		return mathConstantDictionary[ value ]
	return ''

def getEvaluatedNameValue( value, xmlElement ):
	"Evaluate the name value."
	keyValue = KeyValue( value[ len( 'name.' ) : ] )
	if keyValue.value == None:
		return value
	nameElement = xmlElement.getXMLElementByName( keyValue.key )
	return getEvaluatedLinkValueByLookingInDictionary( keyValue.value, nameElement )

def getEvaluatedParentValue( value, xmlElement ):
	"Evaluate the parent value."
	return getEvaluatedLinkValueByLookingInDictionary( value[ len( 'parent.' ) : ], xmlElement.parent )

def getEvaluatedRootValue( value, xmlElement ):
	"Evaluate the parent value."
	return getEvaluatedLinkValueByLookingInDictionary( value[ len( 'root.' ) : ], xmlElement.getRootElement() )

def getEvaluatedSelfValue( value, xmlElement ):
	"Evaluate the self value."
	return getEvaluatedLinkValueByLookingInDictionary( value[ len( 'self.' ) : ], xmlElement )

def getEvaluatedValue( key, xmlElement ):
	"Get the evaluated value."
	if key in xmlElement.attributeDictionary:
		return getEvaluatedValueWithoutChecking( key, xmlElement )
	return None

def getEvaluatedValueWithoutChecking( key, xmlElement ):
	"Get the evaluated value."
	value = str( xmlElement.attributeDictionary[ key ] ).strip()
	if key == 'id':
		return value
	return getEvaluatedLinkValue( value, xmlElement )

def getEvaluatedVertexValue( value, xmlElement ):
	"Evaluate the vertex value."
	vertexIndex = getIntFromFloatString( getEvaluatedLinkValueByLookingInDictionary( value[ len( 'vertex.' ) : ], xmlElement ) )
	vertexElements = xmlElement.getChildrenWithClassName( 'vertex' )
	if vertexIndex >= len( vertexElements ):
		return ''
	if vertexIndex == None:
		print( 'Warning, can not evaluate the vertex string.' )
		print( value )
		return ''
	vector3 = getVector3FromXMLElement( vertexElements[ vertexIndex ] )
	return str( vector3 )

def getFloatIfFloat( value ):
	'Get value as float if its string is a float.'
	if getTypeLength( value ) == - 1:
		return float( value )
	return value

def getFloatListFromBracketedString( bracketedString ):
	"Get list from a bracketed string."
	if not getIsBracketed( bracketedString ):
		return None
	bracketedString = bracketedString.replace( '[', '' ).replace( ']', '' ).replace( '(', '' ).replace( ')', '' )
	splitLine = bracketedString.split( ',' )
	floatList = []
	for word in splitLine:
		evaluatedFloat = getEvaluatedFloatFromValue( word )
		if evaluatedFloat != None:
			floatList.append( evaluatedFloat )
	if len( floatList ) < 1:
		return None
	return floatList

def getHasListEvaluator( evaluators ):
	"Determine if one of the evaluators is list evaluator."
	for evaluator in evaluators:
		if evaluator.__class__ == ListEvaluator:
			return True
	return False

def getKeys( repository ):
	'Get keys for repository.'
	if repository.__class__ == [].__class__:
		return range( len( repository ) )
	if repository.__class__ == {}.__class__:
		return repository.keys()
	return None

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

def getPathByList( vertexList ):
	"Get the paths by list."
	path = []
	for floatList in vertexList:
		vector3 = getVector3ByFloatList( Vector3(), floatList )
		path.append( vector3 )
	return path

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
		print( 'Warning, no path element in geomancer in getPathByKey.' )
		print( pathElement )
		return []
	return pathElement.object.getPaths()[ 0 ]

def getPathByPrefix( path, prefix, xmlElement ):
	"Get path from prefix and xml element."
	if len( path ) < 2:
		print( 'Warning, bug, path is too small in geomancer in setPathByPrefix.' )
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
	"Get the paths by key."
	if key not in xmlElement.attributeDictionary:
		return []
	value = str( xmlElement.attributeDictionary[ key ] ).strip()
	if getStartsWithCurlyEqualRoundSquare( value ):
		value = getEvaluatedExpressionValue( value, xmlElement )
		return getPathsByLists( value )
	pathElement = getXMLElementByValue( value, xmlElement )
	if pathElement == None:
		print( 'Warning, no path element in geomancer in getPathsByKey.' )
		print( pathElement )
		return []
	return pathElement.object.getPaths()

def getPathsByLists( vertexLists ):
	"Get the paths by lists."
	vertexList = vertexLists[ 0 ]
	if len( vertexList ) == 0:
		vertexLists = [ vertexLists ]
	elif vertexList[ 0 ].__class__ != [].__class__:
		vertexLists = [ vertexLists ]
	paths = []
	for vertexList in vertexLists:
		paths.append( getPathByList( vertexList ) )
	return paths

def getSides( radius, xmlElement ):
	"Get the nunber of poygon sides."
	precision = xmlElement.getAttributeValueRecursively( 0.1, 'precision' )
	return math.sqrt( 0.5 * radius * math.pi * math.pi / float( precision ) )

def getSplitDictionary():
	"Get split dictionary."
	splitDictionary = {
		'+' : AdditionEvaluator,
		':' : DictionaryEvaluator,
		'/' : DivisionEvaluator,
		'(' : Evaluator,
		')' : Evaluator,
		'[' : Evaluator,
		']' : Evaluator,
		',' : ListEvaluator,
		'*' : MultiplicationEvaluator,
		'-' : SubtractionEvaluator }
	functionNameString = 'acos asin atan atan2 ceil cos cosh degrees exp fabs floor fmod frexp hypot ldexp log log10 modf pow radians sin sinh sqrt tan tanh'
	functionNames = functionNameString.split()
	for functionName in functionNames:
		splitDictionary[ 'math.' + functionName ] = MathEvaluator
	creatorsDirectoryPath = getCreatorsDirectoryPath()
	pluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( creatorsDirectoryPath )
	for pluginFileName in pluginFileNames:
		splitDictionary[ 'math.' + pluginFileName ] = CreatorEvaluator
	return splitDictionary

def getSolidsDirectoryPath():
	"Get the solids directory path."
	return settings.getPathInFabmetheus( os.path.join( 'fabmetheus_utilities', 'solids' ) )

def getStartsWithCurlyEqualRoundSquare( word ):
	"Determine if the word starts with round or square brackets."
	return word.startswith( '{' ) or word.startswith( '=' ) or word.startswith( '(' ) or word.startswith( '[' )

def getTypeLength( value ):
	"Get the type length of the value."
	if value == None or value == '':
		return 0
	valueString = str( value )
	if valueString.startswith( '{' ) or valueString.startswith( '(' ) or valueString.startswith( '[' ):
		return len( value )
	if getEvaluatedFloatFromValue( value ) == None:
		return 0
	return - 1

def getUniqueToken( line, token ):
	"Get a token which is not in the line."
	while line.find( token ) >= 0:
		token += token[ 216001 % len( token ) ]
	return token

def getVector3ByFloatList( vector3, floatList ):
	"Get vector3 by float list."
	if len( floatList ) > 0:
		vector3.x = floatList[ 0 ]
	if len( floatList ) > 1:
		vector3.y = floatList[ 1 ]
	if len( floatList ) > 2:
		vector3.z = floatList[ 2 ]
	return vector3

def getVector3ByKey( key, vector3, xmlElement ):
	"Get vector3 by key and xml element."
	value = getEvaluatedValue( key, xmlElement )
	if value == None:
		return vector3
	vector3String = str( value ).strip()
	floatList = getFloatListFromBracketedString( vector3String )
	if floatList == None:
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
		return xmlElement.getXMLElementByID( value[ len( 'id.' ) : ] )
	if value.startswith( 'name.' ):
		return xmlElement.getXMLElementByName( value[ len( 'name.' ) : ] )
	if value.startswith( 'parent.' ):
		return xmlElement.parent
	return xmlElement.getXMLElementByName( value )

def processArchivable( archivableClass, xmlElement ):
	"Get any new elements and process the archivable."
	if xmlElement == None:
		return
	getArchivableObject( archivableClass, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processChildren( xmlElement )


class Evaluator:
	'Base evaluator class.'
	def __init__( self, word, xmlElement ):
		'Set value to none.'
		self.value = None
		self.word = word
		self.xmlElement = xmlElement

	def __repr__( self ):
		"Get the string representation of this Evaluator."
		return '%s: %s, %s' % ( self.__class__.__name__, self.word, self.value )

	def convertValueToList( self ):
		'Convert the value into a list.'
		self.value = [ getFloatIfFloat( self.value ) ]

	def executeList( self ):
		'Execute array.'
		self.convertValueToList()

	def executeMath( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		pass

	def executeMinus( self, evaluators, evaluatorIndex ):
		'Minus the value to the right.'
		pass

	def executeOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		pass

	def getFloatValues( self, values ):
		'Add to the float values.'
		if self.value == None or self.value == '':
			return values
		if self.value.__class__ == [].__class__ or self.value.__class__ == {}.__class__:
			return self.value
		return [ getEvaluatedFloatFromValue( self.value ) ]


class AdditionEvaluator( Evaluator ):
	'Class to add two evaluators.'
	def executeOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 20:
			self.executePair( evaluators, evaluatorIndex )

	def executePair( self, evaluators, evaluatorIndex ):
		'Add two evaluators.'
		leftIndex = evaluatorIndex - 1
		rightIndex = evaluatorIndex + 1
		valueIndex = leftIndex
		while evaluators[ valueIndex ].__class__ == self.__class__:
			valueIndex -= 1
		leftValue = evaluators[ valueIndex ].value
		rightValue = leftValue
		if rightIndex < len( evaluators ):
			rightValue = evaluators[ rightIndex ].value
			del evaluators[ rightIndex ]
		operationValue = self.getOperationValue( leftValue, rightValue )
		if valueIndex == leftIndex:
			evaluators[ leftIndex ].value = operationValue
			del evaluators[ evaluatorIndex ]
		else:
			self.value = operationValue

	def getOperationValue( self, leftValue, rightValue ):
		'Add two evaluators.'
		leftLength = getTypeLength( leftValue )
		rightLength = getTypeLength( rightValue )
		if leftLength == 0:
			return rightValue
		if rightLength == 0:
			return leftValue
		if leftLength == - 1 and rightLength == - 1:
			return self.getValueFromValuePair( getEvaluatedFloatFromValue( leftValue ), getEvaluatedFloatFromValue( rightValue ) )
		leftKeys = getKeys( leftValue )
		rightKeys = getKeys( rightValue )
		allKeys = []
		addKeys( leftKeys, allKeys )
		addKeys( rightKeys, allKeys )
		dictionaryClass = {}.__class__
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
		if keys == None:
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


class CreatorEvaluator( Evaluator ):
	'Creator evaluator class.'
	def deleteEvaluatorsSetWithinValuesFunctionName( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		self.functionName = self.word[ len( 'math.' ) : ].lower()
		for deletionIndex in xrange( evaluatorIndex + len( withinEvaluators ) - 1, evaluatorIndex - 1, - 1 ):
			del evaluators[ deletionIndex ]
		self.withinValues = None
		for withinEvaluator in withinEvaluators:
			self.withinValues = withinEvaluator.getFloatValues( self.withinValues )

	def executeMath( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		self.deleteEvaluatorsSetWithinValuesFunctionName( evaluators, evaluatorIndex, withinEvaluators )
		if self.withinValues == None:
			return
		creatorsDirectoryPath = getCreatorsDirectoryPath()
		pluginModule = gcodec.getModuleWithPath( os.path.join( creatorsDirectoryPath, self.functionName ) )
		if pluginModule == None:
			return
		dictionary = {}
		if self.withinValues.__class__ == [].__class__:
			dictionary[ '__list__' ] = self.withinValues
		else:
			dictionary = self.withinValues
		self.value = pluginModule.getGeometryOutput( self.xmlElement.getShallowCopy( dictionary ) )


class DictionaryEvaluator( Evaluator ):
	'Class to join two evaluators.'
	def __init__( self, word, xmlElement ):
		'Set value to none.'
		Evaluator.__init__( self, word, xmlElement )
		self.shouldDictionary = True

	def executeDictionary( self, dictionary, dictionaryEvaluatorIndex, evaluators ):
		'Execute array.'
		self.shouldDictionary = False
		leftValue = evaluators[ dictionaryEvaluatorIndex - 1 ].value
		rightValue = evaluators[ dictionaryEvaluatorIndex + 1 ].value
		dictionary[ leftValue ] = getFloatIfFloat( rightValue )

	def executeOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel != 10:
			return
		if self.shouldDictionary:
			dictionary = {}
			for dictionaryEvaluatorIndex in xrange( len( evaluators ) ):
				dictionaryEvaluator = evaluators[ dictionaryEvaluatorIndex ]
				if dictionaryEvaluator.__class__ == DictionaryEvaluator:
					dictionaryEvaluator.executeDictionary( dictionary, dictionaryEvaluatorIndex, evaluators )
			evaluators[ 0 ].value = dictionary
		for deletionIndex in xrange( len( evaluators ) - 1, evaluatorIndex - 1, - 1 ):
			del evaluators[ deletionIndex ]


class DivisionEvaluator( AdditionEvaluator ):
	'Class to divide two evaluators.'
	def executeOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 40:
			self.executePair( evaluators, evaluatorIndex )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Divide two values.'
		return leftValue / rightValue


class Interpolation:
	"Class to interpolate a path."
	def __init__( self ):
		"Set index."
		self.interpolationIndex = 0

	def getByPrefixX( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element in the z direction."
		if len( path ) < 2:
			print( 'Warning, path is too small in geomancer in Interpolation.' )
			return
		self.path = getPathByPrefix( path, prefix, xmlElement )
		self.interpolationLength = self.path[ - 1 ].x - self.path[ 0 ].x
		self.portionDirections = []
		for point in self.path:
			self.portionDirections.append( PortionDirection( point.x / self.interpolationLength ) )
		return self

	def getByPrefixZ( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element in the z direction."
		if len( path ) < 2:
			print( 'Warning, path is too small in geomancer in Interpolation.' )
			return
		self.path = getPathByPrefix( path, prefix, xmlElement )
		self.interpolationLength = self.path[ - 1 ].z - self.path[ 0 ].z
		self.portionDirections = []
		for point in self.path:
			self.portionDirections.append( PortionDirection( point.z / self.interpolationLength ) )
		return self

	def getComplexByZPortion( self, portion ):
		"Get vector3 from z portion."
		self.setInterpolationIndexByZ( portion )
		innerZPortion = self.getInnerZPortion()
		fromVertex = self.path[ self.interpolationIndex ]
		toVertex = self.path[ self.interpolationIndex + 1 ]
		return ( 1.0 - innerZPortion ) * fromVertex.dropAxis( 2 ) + innerZPortion * toVertex.dropAxis( 2 )

	def getInnerXPortion( self ):
		"Get inner x portion."
		fromVertex = self.path[ self.interpolationIndex ]
		innerLength = self.path[ self.interpolationIndex + 1 ].x - fromVertex.x
		if abs( innerLength ) == 0.0:
			return 0.0
		return ( self.absolutePortion - fromVertex.x ) / innerLength

	def getInnerZPortion( self ):
		"Get inner z portion."
		fromVertex = self.path[ self.interpolationIndex ]
		innerLength = self.path[ self.interpolationIndex + 1 ].z - fromVertex.z
		if abs( innerLength ) == 0.0:
			return 0.0
		return ( self.absolutePortion - fromVertex.z ) / innerLength

	def getVector3ByZPortion( self, portion ):
		"Get vector3 from z portion."
		self.setInterpolationIndexByZ( portion )
		innerZPortion = self.getInnerZPortion()
		fromVertex = self.path[ self.interpolationIndex ]
		toVertex = self.path[ self.interpolationIndex + 1 ]
		return ( 1.0 - innerZPortion ) * fromVertex + innerZPortion * toVertex

	def setInterpolationIndexByX( self, portion ):
		"Set the interpolation index by the x of the path."
		self.absolutePortion = self.path[ 0 ].x + self.interpolationLength * portion
		for self.interpolationIndex in xrange( 0, len( self.path ) - 1 ):
			beginX = self.path[ self.interpolationIndex ].x
			endX = self.path[ self.interpolationIndex + 1 ].x
			if beginX <= self.absolutePortion and endX >= self.absolutePortion:
				return

	def setInterpolationIndexByZ( self, portion ):
		"Set the interpolation index by the z of the path."
		self.absolutePortion = self.path[ 0 ].z + self.interpolationLength * portion
		for self.interpolationIndex in xrange( 0, len( self.path ) - 1 ):
			beginZ = self.path[ self.interpolationIndex ].z
			endZ = self.path[ self.interpolationIndex + 1 ].z
			if beginZ <= self.absolutePortion and endZ >= self.absolutePortion:
				return

	def getYByXPortion( self, portion ):
		"Get y from x portion."
		self.setInterpolationIndexByX( portion )
		innerXPortion = self.getInnerXPortion()
		fromVertex = self.path[ self.interpolationIndex ]
		toVertex = self.path[ self.interpolationIndex + 1 ]
		return ( 1.0 - innerXPortion ) * fromVertex.y + innerXPortion * toVertex.y


class KeyValue:
	"Class to hold a key value."
	def __init__( self, line ):
		"Get key value."
		self.value = None
		dotIndex = line.find( '.' )
		if dotIndex < 0:
			self.key = line
			return
		self.key = line[ : dotIndex ]
		self.value = line[ dotIndex + 1 : ]


class ListEvaluator( AdditionEvaluator ):
	'Class to join two evaluators.'
	def __init__( self, word, xmlElement ):
		'Set value to none.'
		Evaluator.__init__( self, word, xmlElement )
		self.shouldList = True

	def executeList( self ):
		'Execute array.'
		self.shouldList = False

	def executeOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel != 0:
			return
		if self.shouldList:
			for evaluator in evaluators:
				evaluator.executeList()
		self.executePair( evaluators, evaluatorIndex )

	def getOperationValue( self, leftValue, rightValue ):
		'Join two values.'
		return leftValue + rightValue


class MathEvaluator( CreatorEvaluator ):
	'Math evaluator class.'
	def executeMath( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		self.deleteEvaluatorsSetWithinValuesFunctionName( evaluators, evaluatorIndex, withinEvaluators )
		function = math.__dict__[ self.functionName ]
		while len( self.withinValues ) > 0:
			try:
				self.value = function( *self.withinValues )
				return
			except:
				self.withinValues = self.withinValues[ : - 1 ]
		print( 'Warning, the MathEvaluator in geomancer can not handle:' )
		print( self.functionName )
		print( self.withinValues )


class MultiplicationEvaluator( DivisionEvaluator ):
	'Class to multiply two evaluators.'
	def getValueFromValuePair( self, leftValue, rightValue ):
		'Multiply two values.'
		return leftValue * rightValue


class NumericEvaluator( Evaluator ):
	'Class to evaluate a string.'
	def __init__( self, word, xmlElement ):
		'Set value.'
		valueString = str( getEvaluatedLinkValue( word, xmlElement ) )
		self.word = word
		self.value = getEvaluatedLinkValue( valueString, xmlElement )


class PortionDirection:
	"Class to hold a portion and direction."
	def __init__( self, portion ):
		"Initialize."
		self.direction = False
		self.portion = portion

	def __repr__( self ):
		"Get the string representation of this PortionDirection."
		return '%s: %s' % ( self.portion, self.direction )


class PowerEvaluator( AdditionEvaluator ):
	'Class to power two evaluators.'
	def executeOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 60:
			self.executePair( evaluators, evaluatorIndex )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Power of two values.'
		return math.pow( leftValue, rightValue )


class SubtractionEvaluator( AdditionEvaluator ):
	'Class to subtract two evaluators.'
	def executeMinus( self, evaluators, evaluatorIndex ):
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

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Subtract two values.'
		return leftValue - rightValue

	def getNegativeValue( self, value ):
		'Get the negative value.'
		typeLength = getTypeLength( value )
		if typeLength < 0:
			return - float( value )
		if typeLength == 0:
			return None
		for key in getKeys( value ):
			value[ key ] = self.getNegativeValue( value[ key ] )
		return value


globalSplitDictionary = getSplitDictionary()
