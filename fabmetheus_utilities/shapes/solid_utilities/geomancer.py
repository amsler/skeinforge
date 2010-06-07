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
from fabmetheus_utilities import xml_simple_parser
import math
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


powerToken = '__PoweR_syMbol__toKen___For_DouBle_asterisk__'


def addEvaluator( evaluators, word, xmlElement ):
	"Get the evaluator."
	global globalSplitDictionary
	if word in globalSplitDictionary:
		evaluators.append( globalSplitDictionary[ word ]( word, xmlElement ) )
		return
	if word.startswith( 'function.' ):
		evaluators.append( FunctionEvaluator( word, xmlElement ) )
		return
	if word.startswith( 'local.' ):
		evaluators.append( LocalEvaluator( word, xmlElement ) )
		return
	evaluators.append( NumericEvaluator( word, xmlElement ) )

def addKeys( fromKeys, toKeys ):
	'Add keys from the list to the list.'
	for fromKey in fromKeys:
		if fromKey not in toKeys:
			toKeys.append( fromKey )

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
			if returnValue != None:
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
			dictionary[ key ] = [ float( value.x ), float( value.y ), float( value.z ) ]
		else:
			convertToFloatList( dictionary[ key ] )

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
				valueString = str(xmlElement.attributeDictionary[ key ]  )
				print( 'Warning, %s does not evaluate.' % valueString )
				evaluatedDictionary[ key + '__Warning__' ] = 'Can not evaluate: ' + valueString
			else:
				evaluatedDictionary[ key ] = value
	return evaluatedDictionary

def getEvaluatedExpressionValue( value, xmlElement ):
	"Evaluate the expression value."
	return getEvaluatedExpressionValueBySplitLine( getEvaluatorSplitLine( value, xmlElement ), xmlElement )

def getEvaluatedExpressionValueBySplitLine( splitLine, xmlElement ):
	"Evaluate the expression value."
	evaluators = []
	for word in splitLine:
		addEvaluator( evaluators, word, xmlElement )
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

def getEvaluatedIDValue( value, xmlElement ):
	"Evaluate the id value."
	keyValue = KeyValue().getByDot( value[ len( 'id.' ) : ] )
	if keyValue.value == None:
		return value
	idElement = xmlElement.getXMLElementByID( keyValue.key )
	return getEvaluatedLinkValueByLookingInDictionary( keyValue.value, idElement )

def getEvaluatedLinkValue( value, xmlElement ):
	"Get the evaluated link value."
	if value.startswith( 'id.' ):
		return getEvaluatedIDValue( value, xmlElement )
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

def getEvaluatedNameValue( value, xmlElement ):
	"Evaluate the name value."
	keyValue = KeyValue().getByDot( value[ len( 'name.' ) : ] )
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
		return getEvaluatedValueObliviously( key, xmlElement )
	return None

def getEvaluatedValueObliviously( key, xmlElement ):
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

def getEvaluatorSplitLine( value, xmlElement ):
	"Get split line for evaluators."
	if value.startswith( '=' ):
		value = value[ len( '=' ) : ]
	splitToken = getUniqueToken( value, '_SpliT_' )
	global powerToken
	value = value.replace( '**', powerToken ).replace( '{', '(' ).replace( '}', ')' )
	global globalSplitDictionaryOperator
	for splitDictionaryOperatorKey in globalSplitDictionaryOperator.keys():
		value = value.replace( splitDictionaryOperatorKey, splitToken + splitDictionaryOperatorKey + splitToken )
	evaluatorSplitLine = []
	for word in value.split( splitToken ):
		strippedWord = word.strip()
		if strippedWord != '':
			evaluatorSplitLine.append( strippedWord )
	return evaluatorSplitLine

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

def getFunctionByValue( value, xmlElement ):
	"Get function by value from the xmlElement."
	xmlElement = getXMLElementByValue( value[ len( 'function.' ) : ], xmlElement )
	if xmlElement == None:
		print( 'Warning, function %s could not be found in element:' % value )
		print( xmlElement )
		return None
	if xmlElement.object == None:
		if 'return' in xmlElement.attributeDictionary:
			value = xmlElement.attributeDictionary[ 'return' ]
			xmlElement.object = getEvaluatorSplitLine( value, xmlElement )
		else:
			xmlElement.object = []
	return Function( xmlElement.object, xmlElement )

def getHasListEvaluator( evaluators ):
	"Determine if one of the evaluators is list evaluator."
	for evaluator in evaluators:
		if evaluator.__class__ == ListEvaluator:
			return True
	return False

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
	addPrefixDictionary( splitDictionary, globalMathConstantDictionary.keys(), 'math.', ConstantEvaluator )
	pluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( getCreationDirectoryPath() )
	addPrefixDictionary( splitDictionary, pluginFileNames, 'math.', CreationEvaluator )
	functionNameString = 'acos asin atan atan2 ceil cos cosh degrees exp fabs floor fmod frexp hypot ldexp log log10 modf pow radians sin sinh sqrt tan tanh'
	addPrefixDictionary( splitDictionary, functionNameString.split(), 'math.', MathEvaluator )
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

def getUniqueToken( line, token ):
	"Get a token which is not in the line."
	while line.find( token ) >= 0:
		token += token[ 216001 % len( token ) ]
	return token

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
		return xmlElement.getXMLElementByID( value[ len( 'id.' ) : ] )
	if value.startswith( 'name.' ):
		return xmlElement.getXMLElementByName( value[ len( 'name.' ) : ] )
	if value.startswith( 'parent.' ):
		return xmlElement.parent
	return xmlElement.getXMLElementByName( value )

def processArchivable( archivableClass, xmlElement, xmlProcessor ):
	"Get any new elements and process the archivable."
	if xmlElement == None:
		return
	getArchivableObject( archivableClass, xmlElement )
	xmlProcessor.processChildren( xmlElement )


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
		if self.value.__class__ == list or self.value.__class__ == dict:
			return self.value
		return [ euclidean.getFloatFromValue( self.value ) ]


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
			return self.getValueFromValuePair( euclidean.getFloatFromValue( leftValue ), euclidean.getFloatFromValue( rightValue ) )
		leftKeys = getKeys( leftValue )
		rightKeys = getKeys( rightValue )
		allKeys = []
		addKeys( leftKeys, allKeys )
		addKeys( rightKeys, allKeys )
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


class ConstantEvaluator( Evaluator ):
	'Class to evaluate a string.'
	def __init__( self, word, xmlElement ):
		'Set value.'
		self.word = word
		global globalMathConstantDictionary
		self.value = globalMathConstantDictionary[ word[ len( 'math.' ) : ] ]


class CreationEvaluator( Evaluator ):
	'Creation evaluator class.'
	def deleteEvaluatorsSetWithinValuesFunctionName( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		for deletionIndex in xrange( evaluatorIndex + len( withinEvaluators ) - 1, evaluatorIndex - 1, - 1 ):
			del evaluators[ deletionIndex ]
		self.withinValues = []
		for withinEvaluator in withinEvaluators:
			self.withinValues = withinEvaluator.getFloatValues( self.withinValues )

	def executeMath( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		self.deleteEvaluatorsSetWithinValuesFunctionName( evaluators, evaluatorIndex, withinEvaluators )
		pluginModule = gcodec.getModuleWithPath( os.path.join( getCreationDirectoryPath(), self.getFunctionName() ) )
		if pluginModule == None:
			return
		dictionary = {}
		if self.withinValues != None:
			if self.withinValues.__class__ == list:
				dictionary[ '_arguments' ] = self.withinValues
			else:
				dictionary = self.withinValues
		self.value = pluginModule.getGeometryOutput( self.xmlElement.getShallowCopy( dictionary ) )
		convertToFloatList( self.value )

	def getFunctionName( self ):
		'Get the function name.'
		return self.word[ len( 'math.' ) : ].lower()


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


class EquationResult:
	"Class to get equation results."
	def __init__( self, key, xmlElement ):
		"Initialize."
		value = xmlElement.attributeDictionary[ key ]
		if value.startswith( 'function.' ):
			self.function = getFunctionByValue( value, xmlElement )
			return
		self.function = Function( getEvaluatorSplitLine( value, xmlElement ), {}, xmlElement )

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
		self.xmlProcessor = xmlElement.getRootElement().xmlProcessor
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
		del self.xmlElement.getRootElement().xmlProcessor.functions[ - 1 ]


class FunctionEvaluator( CreationEvaluator ):
	'Function evaluator class.'
	def executeMath( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the function statement and delete the evaluators. later parameters'
		self.deleteEvaluatorsSetWithinValuesFunctionName( evaluators, evaluatorIndex, withinEvaluators )
		self.function = getFunctionByValue( self.word, self.xmlElement )
		self.setFunctionLocalTable()
		if self.function == None:
			print( 'Warning, the FunctionEvaluator in geomancer can not handle:' )
			print( self.word )
			print( self.withinValues )
			print( self.xmlElement.attributeDictionary )
			return
		self.value = self.function.getReturnValue()

	def setFunctionLocalTable( self ):
		'Set the local table for the function.'
		if self.withinValues == None:
			return
		self.function.localTable[ '_arguments' ] = self.withinValues
		if self.withinValues.__class__ == dict:
			self.function.localTable = self.withinValues
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
			if parameterWordIndex < len( self.withinValues ):
				self.function.localTable[ keyValue.key ] = self.withinValues[ parameterWordIndex ]
			else:
				strippedValue = keyValue.value
				if strippedValue == None:
					print( 'Warning there is no default parameter in getParameterValue for:' )
					print( strippedWord )
					print( parameterWords )
					print( self.withinValues )
					print( self.function.xmlElement.attributeDictionary )
				else:
					strippedValue = strippedValue.strip()
				self.function.localTable[ keyValue.key.strip() ] = strippedValue
		if len( self.withinValues ) > len( parameterWords ):
			print( 'Warning there are too many function parameters for:' )
			print( self.function.xmlElement.attributeDictionary )
			print( parameterWords )
			print( self.withinValues )

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
			print( 'Warning, path is too small in geomancer in Interpolation.' )
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
			print( 'Warning, path is too small in geomancer in Interpolation.' )
			return
		self.path = getPathByPrefix( path, prefix, xmlElement )
		self.distances = []
		for point in self.path:
			self.distances.append( point.x )
		return self.getByDistances()

	def getByPrefixZ( self, path, prefix, xmlElement ):
		"Get interpolation from prefix and xml element in the z direction."
		if len( path ) < 2:
			print( 'Warning, path is too small in geomancer in Interpolation.' )
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


class LocalEvaluator( CreationEvaluator ):
	'Class to get a local variable.'
	def __init__( self, word, xmlElement ):
		'Set value.'
		self.word = word
		self.value = None
		functions = xmlElement.getRootElement().xmlProcessor.functions
		if len( functions ) < 1:
			return
		localTable = functions[ - 1 ].localTable
		suffix = word[ len( 'local.' ) : ]
		if suffix in localTable:
			self.value = localTable[ suffix ]

	def executeMath( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		if self.value.__class__ != list:
			return
		self.deleteEvaluatorsSetWithinValuesFunctionName( evaluators, evaluatorIndex, withinEvaluators )
		if len( self.withinValues ) < 1:
			return
		arrayIndexFloat = euclidean.getFloatFromValue( self.withinValues[ 0 ] )
		if arrayIndexFloat == None:
			return
		self.value = self.value[ int( round( arrayIndexFloat ) ) ]


class MathEvaluator( CreationEvaluator ):
	'Math evaluator class.'
	def executeMath( self, evaluators, evaluatorIndex, withinEvaluators ):
		'Evaluate the math statement and delete the evaluators.'
		self.deleteEvaluatorsSetWithinValuesFunctionName( evaluators, evaluatorIndex, withinEvaluators )
		function = math.__dict__[ self.getFunctionName() ]
		while len( self.withinValues ) > 0:
			try:
				self.value = function( *self.withinValues )
				return
			except:
				self.withinValues = self.withinValues[ : - 1 ]
		print( 'Warning, the MathEvaluator in geomancer can not handle:' )
		print( self.getFunctionName() )
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
		self.directionReversed = False
		self.portion = portion

	def __repr__( self ):
		"Get the string representation of this PortionDirection."
		return '%s: %s' % ( self.portion, self.directionReversed )


class PowerEvaluator( AdditionEvaluator ):
	'Class to power two evaluators.'
	def executeOperation( self, evaluators, evaluatorIndex, operationLevel ):
		'Operate on two evaluators.'
		if operationLevel == 60:
			self.executePair( evaluators, evaluatorIndex )

	def getValueFromValuePair( self, leftValue, rightValue ):
		'Power of two values.'
		return math.pow( leftValue, rightValue )


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


globalSplitDictionaryOperator = {
		'+' : AdditionEvaluator,
		':' : DictionaryEvaluator,
		'/' : DivisionEvaluator,
		'(' : Evaluator,
		')' : Evaluator,
		'[' : Evaluator,
		']' : Evaluator,
		',' : ListEvaluator,
		'*' : MultiplicationEvaluator,
		powerToken : PowerEvaluator,
		'-' : SubtractionEvaluator }
#Constants from: http://www.physlink.com/reference/MathConstants.cfm
globalMathConstantDictionary = {
		'e' : math.e,
		'euler' : 0.5772156649015328606065120,
		'golden' : 1.6180339887498948482045868,
		'pi' : math.pi }
#If anyone wants to add stuff, more constants are at: http://en.wikipedia.org/wiki/Mathematical_constant
globalSplitDictionary = getSplitDictionary()
