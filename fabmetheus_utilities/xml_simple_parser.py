"""
The xml_simple_parser.py script is an xml parser that can parse a line separated xml text.

This xml parser will read a line seperated xml text and produce a tree of the xml with a root element.  Each element can have an attribute table, children, a class name, parent, text and a link to the root element.

This example gets an xml tree for the xml file boolean.xml.  This example is run in a terminal in the folder which contains boolean.xml and xml_simple_parser.py.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> file = open( 'boolean.xml', 'r' )
>>> xmlText = file.read()
>>> file.close()
>>> from xml_simple_parser import XMLSimpleParser
>>> xmlParser = XMLSimpleParser( None, xmlText )
>>> print( xmlParser )
  ?xml, {'version': '1.0'}
  ArtOfIllusion, {'xmlns:bf': '//babelfiche/codec', 'version': '2.0', 'fileversion': '3'}
  Scene, {'bf:id': 'theScene'}
  materials, {'bf:elem-type': 'java.lang.Object', 'bf:list': 'collection', 'bf:id': '1', 'bf:type': 'java.util.Vector'}
..
many more lines of the xml tree
..

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import xml_simple_writer
import cStringIO


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


class XMLElement:
	"An xml element."
	def __init__( self ):
		"Add empty lists."
		self.attributeDictionary = {}
		self.children = []
		self.className = ''
		self.idDictionary = {}
		self.importName = ''
		self.nameDictionary = {}
		self.object = None
		self.parent = None
		self.text = ''

	def __repr__( self ):
		"Get the string representation of this XML element."
		return str( self.attributeDictionary )

	def addAttribute( self, beforeQuote, withinQuote ):
		"Add the attribute to the dictionary."
		beforeQuote = beforeQuote.strip()
		lastEqualIndex = beforeQuote.rfind( '=' )
		if lastEqualIndex < 0:
			return
		key = beforeQuote[ : lastEqualIndex ].strip()
		self.attributeDictionary[ key ] = withinQuote

	def addToIDDictionary( self, idKey, xmlElement ):
		"Add to the id dictionary of all the XMLProcessor."
		self.getRoot().idDictionary[ idKey ] = xmlElement

	def addToIDDictionaryIFIDExists( self ):
		"Add to the id dictionary if the id key exists in the attribute dictionary."
		self.importName = self.getCascadeImportName()
		if 'id' in self.attributeDictionary:
			self.addToIDDictionary( self.getImportNameWithDot() + self.attributeDictionary[ 'id' ], self )
		if 'name' in self.attributeDictionary:
			self.addToNameDictionary( self.getImportNameWithDot() + self.attributeDictionary[ 'name' ], self )

	def addToNameDictionary( self, name, xmlElement ):
		"Add to the name dictionary of all the XMLProcessor."
		self.getRoot().nameDictionary[ name ] = xmlElement

	def addXML( self, depth, output ):
		"Add xml for this object."
		xml_simple_writer.addBeginXMLTag( self.attributeDictionary, depth, self.className, output )
		xml_simple_writer.addXMLFromObjects( depth + 1, self.children, output )
		xml_simple_writer.addEndXMLTag( depth, self.className, output )

	def copyXMLChildren( self, idSuffix, parent ):
		"Copy the xml children."
		for child in self.children:
			child.getCopy( idSuffix, parent )

	def getByParent( self, parent ):
		"Get xmlElement and add it to the parent."
		self.parent = parent
		parent.children.append( self )
		return self

	def getCascadeFloat( self, defaultFloat, key ):
		"Get the cascade float."
		return euclidean.getFloatFromValue( self.getCascadeValue( defaultFloat, key ) )

	def getCascadeImportName( self ):
		"Get the cascade import file name."
		if self.importName != '':
			return self.importName
		if self.parent == None:
			return ''
		return self.parent.getCascadeImportName()

	def getCascadeValue( self, defaultValue, key ):
		"Get the cascade value."
		if key in self.attributeDictionary:
			return self.attributeDictionary[ key ]
		if self.parent == None:
			return defaultValue
		return self.parent.getCascadeValue( defaultValue, key )

	def getChildrenWithClassName( self, className ):
		"Get the children which have the given class name."
		childrenWithClassName = []
		for child in self.children:
			if className == child.className:
				childrenWithClassName.append( child )
		return childrenWithClassName

	def getCopy( self, idSuffix, parent ):
		"Copy the xml element and add it to the parent."
		copy = XMLElement().getByParent( parent )
		copy.attributeDictionary = self.attributeDictionary.copy()
		if idSuffix != '':
			if 'id' in copy.attributeDictionary:
				copy.attributeDictionary[ 'id' ] = copy.attributeDictionary[ 'id' ] + idSuffix
		copy.className = self.className
		copy.text = self.text
		copy.addToIDDictionaryIFIDExists()
		self.copyXMLChildren( idSuffix, copy )
		return copy

	def getFirstChildWithClassName( self, className ):
		"Get the first child which has the given class name."
		for child in self.children:
			if className == child.className:
				return child
		return None

	def getIDSuffix( self, elementIndex = None ):
		"Get the id suffix from the dictionary."
		suffix = self.className
		if 'id' in self.attributeDictionary:
			suffix = self.attributeDictionary[ 'id' ]
		if elementIndex == None:
			return '_%s' % suffix
		return '_%s_%s' % ( suffix, elementIndex )

	def getImportNameWithDot( self ):
		"Get import name with dot."
		if self.importName == '':
			return ''
		return self.importName + '.'

	def getParentParseReplacedLine( self, line, parent ):
		"Parse replaced line."
		if line[ : len( '</' ) ] == '</':
			if parent == None:
				return parent
			return parent.parent
		self.setParentAddToChildren( parent )
		self.className = line[ 1 : line.replace( '>', ' ' ).find( ' ' ) ]
		lastWord = line[ - 2 : ]
		splitLine = line.replace( '">', '" > ' ).split()
		lineAfterClassName = line[ 2 + len( self.className ) : - 1 ]
		beforeQuote = ''
		lastQuoteCharacter = None
		withinQuote = ''
		for characterIndex in xrange( len( lineAfterClassName ) ):
			character = lineAfterClassName[ characterIndex ]
			if lastQuoteCharacter == None:
				if character == '"' or character == "'":
					lastQuoteCharacter = character
					character = ''
			if character == lastQuoteCharacter:
				self.addAttribute( beforeQuote, withinQuote )
				beforeQuote = ''
				lastQuoteCharacter = None
				withinQuote = ''
				character = ''
			if lastQuoteCharacter == None:
				beforeQuote += character
			else:
				withinQuote += character
		self.addToIDDictionaryIFIDExists()
		if lastWord == '/>':
			return parent
		tagEnd = '</%s>' % self.className
		if line[ - len( tagEnd ) : ] == tagEnd:
			untilTagEnd = line[ : - len( tagEnd ) ]
			lastGreaterThanIndex = untilTagEnd.rfind( '>' )
			self.text = untilTagEnd[ lastGreaterThanIndex + 1 : ]
			return parent
		return self

	def getRoot( self ):
		"Get the root element."
		if self.parent == None:
			return self
		return self.parent.getRoot()

	def getShallowCopy( self, attributeDictionary ):
		"Copy the xml element and set its dictionary."
		shallowCopy = XMLElement()
		shallowCopy.attributeDictionary = attributeDictionary
		shallowCopy.children = self.children
		shallowCopy.className = self.className
		shallowCopy.idDictionary = self.idDictionary
		shallowCopy.importName = self.importName
		shallowCopy.object = self.object
		shallowCopy.nameDictionary = self.nameDictionary
		shallowCopy.parent = self.parent
		shallowCopy.text = self.text
		return shallowCopy

	def getSubChildWithID( self, idReference ):
		"Get the child which has the idReference."
		for child in self.children:
			if 'bf:id' in child.attributeDictionary:
				if child.attributeDictionary[ 'bf:id' ] == idReference:
					return child
			subChildWithID = child.getSubChildWithID( idReference )
			if subChildWithID != None:
				return subChildWithID
		return None

	def getValueByKey( self, key ):
		"Get value by the key."
		if key in evaluate.globalElementValueDictionary:
			return evaluate.globalElementValueDictionary[ key ]( self )
		if key in self.attributeDictionary:
			return evaluate.getEvaluatedLinkValue( self.attributeDictionary[ key ], self )
		return None

	def getXMLElementByID( self, idKey ):
		"Get the xml element by id."
		idDictionary = self.getRoot().idDictionary
		if idKey in idDictionary:
			return idDictionary[ idKey ]
		return None

	def getXMLElementByImportID( self, idKey ):
		"Get the xml element by import file name and id."
		return self.getXMLElementByID( self.getImportNameWithDot() + idKey )

	def getXMLElementByImportName( self, name ):
		"Get the xml element by import file name and name."
		return self.getXMLElementByName( self.getImportNameWithDot() + name )

	def getXMLElementByName( self, name ):
		"Get the xml element by name."
		nameDictionary = self.getRoot().nameDictionary
		if name in nameDictionary:
			return nameDictionary[ name ]
		return None

	def getXMLProcessor( self ):
		"Get the xmlProcessor."
		return self.getRoot().xmlProcessor

	def setParentAddToChildren( self, parent ):
		"Set the parent and add this to its children."
		self.parent = parent
		if self.parent != None:
			self.parent.children.append( self )


class XMLSimpleParser:
	"A simple xml parser."
	def __init__( self, fileName, parent, xmlText ):
		"Add empty lists."
		self.commentString = None
		self.fileName = fileName
		self.isInComment = False
		self.parent = parent
		self.root = None
		self.xmlText = xmlText
		self.lines = gcodec.getTextLines( xmlText )
		for line in self.lines:
			self.parseLine( line )
	
	def __repr__( self ):
		"Get the string representation of this parser."
		return str( self.root )

	def getRoot( self ):
		"Get the root element."
		return self.root

	def parseLine( self, line ):
		"Parse an xml line and add it to the xml tree."
		lineStripped = line.lstrip()
		if len( lineStripped ) < 1:
			return
		if self.root == None:
			if lineStripped.startswith( '<?xml' ):
				return
		if lineStripped[ : len( '<!--' ) ] == '<!--':
			self.commentString = ''
		if self.commentString != None:
			self.commentString += line + '\n'
			if lineStripped.find( '-->' ) != - 1:
				xmlElement = XMLElement()
				xmlElement.attributeDictionary[ 'comment' ] = self.commentString
				xmlElement.className = 'comment'
				xmlElement.setParentAddToChildren( self.parent )
				self.commentString = None
				return
		if self.commentString != None:
			return
		xmlElement = XMLElement()
		self.parent = xmlElement.getParentParseReplacedLine( lineStripped, self.parent )
		if self.root == None:
			self.root = xmlElement
			self.root.parser = self
