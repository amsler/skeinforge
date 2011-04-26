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

from fabmetheus_utilities import gcodec
from fabmetheus_utilities import xml_simple_writer


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
		self.object = None
		self.parent = None
		self.text = ''

	def __repr__( self ):
		"Get the string representation of this XML element."
		output = xml_simple_writer.getBeginXMLOutput()
		self.addXML( 0, output )
		return output.getvalue()

	def addAttribute( self, characterIndex, line ):
		"Add the attribute to the dictionary."
		beforeEqualLine = line[ : characterIndex ][ : : - 1 ]
		lineStripped = beforeEqualLine.lstrip().replace( '"', ' ' ).replace( "'", ' ' )
		firstWord = lineStripped.split()[ 0 ]
		key = firstWord[ : : - 1 ]
		self.attributeDictionary[ key ] = self.getWordWithinQuotes( line[ characterIndex + 1 : ] )

	def addIDIfUndefined( self, idHint ):
		"Add the id if the id is undefined."
		if 'id' in self.attributeDictionary:
			return
		uniqueID = self.getUniqueID( idHint )
		self.attributeDictionary[ 'id' ] = uniqueID
		self.addToIDDictionary( self )

	def addToIDDictionary( self, xmlElement ):
		"Add to the id dictionary of all the parents."
		self.idDictionary[ xmlElement.attributeDictionary[ 'id' ] ] = xmlElement
		if self.parent != None:
			self.parent.addToIDDictionary( xmlElement )

	def addToIDDictionaryIFIDExists( self ):
		"Add to the id dictionary if the id key exists in the attribute dictionary."
		if 'id' in self.attributeDictionary:
			self.addToIDDictionary( self )

	def addXML( self, depth, output ):
		"Add xml for this object."
		xml_simple_writer.addBeginXMLTag( self.attributeDictionary, depth, self.className, output )
		xml_simple_writer.addXMLFromObjects( depth + 1, self.children, output )
		xml_simple_writer.addEndXMLTag( depth, self.className, output )

	def copyXMLChildren( self, parent ):
		"Copy the xml children."
		for child in self.children:
			child.getCopy( '', parent )

	def getChildrenWithClassName( self, className ):
		"Get the children which have the given class name."
		childrenWithClassName = []
		for child in self.children:
			if className == child.className:
				childrenWithClassName.append( child )
		return childrenWithClassName

	def getCopy( self, idHint, parent ):
		"Copy the xml element and add it to the parent."
		copy = XMLElement()
		copy.attributeDictionary = self.attributeDictionary.copy()
		copy.className = self.className
		copy.parent = parent
		copy.text = self.text
		parent.children.append( copy )
		if idHint == '':
			if 'id' in copy.attributeDictionary:
				idHint = copy.attributeDictionary[ 'id' ]
		if idHint != '':
			copy.attributeDictionary[ 'id' ] = self.getUniqueID( idHint )
			copy.addToIDDictionary( copy )
		self.copyXMLChildren( copy )
		return copy

	def getFirstChildWithClassName( self, className ):
		"Get the first child which has the given class name."
		for child in self.children:
			if className == child.className:
				return child
		return None

	def getParentParseReplacedLine( self, line, parent ):
		"Parse replaced line."
		if line[ : len( '</' ) ] == '</':
			if parent == None:
				return parent
			return parent.parent
		self.parent = parent
		self.className = line[ 1 : line.replace( '>', ' ' ).find( ' ' ) ]
		lastWord = line[ - 2 : ]
		splitLine = line.replace( '">', '" > ' ).split()
		lineAfterClassName = line[ 2 + len( self.className ) : - 2 ]
		for characterIndex in xrange( len( lineAfterClassName ) ):
			if lineAfterClassName[ characterIndex ] == '=':
				self.addAttribute( characterIndex, lineAfterClassName )
		if self.parent != None:
			self.parent.children.append( self )
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

	def getRootElement( self ):
		"Get the root element."
		if self.parent == None:
			return self
		return self.parent.getRootElement()

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

	def getUniqueID( self, idHint ):
		"Get a unique id from the hint."
		rootDictionary = self.getRootElement().idDictionary
		if idHint not in rootDictionary:
			return idHint
		idHintIndex = 1
		while 1:
			uniqueID = '%s__%s' % ( idHint, idHintIndex )
			if uniqueID not in rootDictionary:
				return uniqueID
			idHintIndex += 1

	def getWordWithinQuotes( self, line ):
		"Get the word within the quotes."
		quoteCharacter = None
		word = ''
		for character in line:
			if character == '"' or character == "'":
				if quoteCharacter == None:
					quoteCharacter = character
				else:
					return word
			elif quoteCharacter != None:
				word += character
		return word


class XMLSimpleParser:
	"A simple xml parser."
	def __init__( self, fileName, parent, xmlText ):
		"Add empty lists."
		self.fileName = fileName
		self.isInComment = False
		self.parent = parent
		self.rootElement = None
		self.xmlText = xmlText
		self.lines = gcodec.getTextLines( xmlText )
		for line in self.lines:
			self.parseLine( line )
	
	def __repr__( self ):
		"Get the string representation of this parser."
		return str( self.rootElement )

	def getRootElement( self ):
		"Get the root element."
		return self.rootElement

	def parseLine( self, line ):
		"Parse a gcode line and add it to the inset skein."
		lineStripped = line.lstrip()
		if len( lineStripped ) < 1:
			return
		if self.rootElement == None:
			if gcodec.getHasPrefix( lineStripped, '<?xml' ):
				return
		if lineStripped[ : len( '<!--' ) ] == '<!--':
			self.isInComment = True
		if self.isInComment:
			if lineStripped.find( '-->' ) != - 1:
				self.isInComment = False
				return
		if self.isInComment:
			return
		xmlElement = XMLElement()
		self.parent = xmlElement.getParentParseReplacedLine( lineStripped, self.parent )
		if self.rootElement == None:
			self.rootElement = xmlElement
			self.rootElement.parser = self
