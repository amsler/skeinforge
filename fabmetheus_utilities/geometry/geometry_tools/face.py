"""
Face of a triangle mesh.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_tools import matrix4x4
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities.vector3index import Vector3Index
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
from fabmetheus_utilities import xml_simple_parser
from fabmetheus_utilities import xml_simple_writer
import cmath
import cStringIO
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def addGeometryList( faces, xmlElement ):
	"Add vertex elements to an xml element."
	for face in faces:
		faceElement = xml_simple_parser.XMLElement()
		face.addToAttributeDictionary( faceElement.attributeDictionary )
		faceElement.className = 'face'
		faceElement.parent = xmlElement
		xmlElement.children.append( faceElement )

def getCommonVertexIndex( edgeFirst, edgeSecond ):
	"Get the vertex index that both edges have in common."
	for edgeFirstVertexIndex in edgeFirst.vertexIndexes:
		if edgeFirstVertexIndex == edgeSecond.vertexIndexes[ 0 ] or edgeFirstVertexIndex == edgeSecond.vertexIndexes[ 1 ]:
			return edgeFirstVertexIndex
	print( "Inconsistent GNU Triangulated Surface" )
	print( edgeFirst )
	print( edgeSecond )
	return 0

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	face = Face()
	face.index = len( xmlElement.parent.object.faces )
	for vertexIndexIndex in xrange( 3 ):
		face.vertexIndexes.append( evaluate.getEvaluatedInt( 'vertex' + str( vertexIndexIndex ), xmlElement ) )
	xmlElement.parent.object.faces.append( face )


class Edge:
	"An edge of a triangle mesh."
	def __init__( self ):
		"Set the face indexes to None."
		self.faceIndexes = []
		self.vertexIndexes = []
		self.zMaximum = None
		self.zMinimum = None
	
	def __repr__( self ):
		"Get the string representation of this Edge."
		return str( self.index ) + ' ' + str( self.faceIndexes ) + ' ' + str( self.vertexIndexes )

	def addFaceIndex( self, faceIndex ):
		"Add first None face index to input face index."
		self.faceIndexes.append( faceIndex )

	def getFromVertexIndexes( self, edgeIndex, vertexIndexes ):
		"Initialize from two vertex indices."
		self.index = edgeIndex
		self.vertexIndexes = vertexIndexes[ : ]
		self.vertexIndexes.sort()
		return self


class Face:
	"A face of a triangle mesh."
	def __init__( self ):
		"Set the edge indexes to None."
		self.edgeIndexes = []
		self.index = None
		self.vertexIndexes = []

	def __repr__( self ):
		"Get the string representation of this object info."
		output = cStringIO.StringIO()
		self.addXML( 2, output )
		return output.getvalue()

	def addToAttributeDictionary( self, attributeDictionary ):
		"Add to the attribute dictionary."
		for vertexIndexIndex in xrange( len( self.vertexIndexes ) ):
			vertexIndex = self.vertexIndexes[ vertexIndexIndex ]
			attributeDictionary[ 'vertex' + str( vertexIndexIndex ) ] = str( vertexIndex )

	def addXML( self, depth, output ):
		"Add the xml for this object."
		attributeDictionary = {}
		self.addToAttributeDictionary( attributeDictionary )
		xml_simple_writer.addClosedXMLTag( attributeDictionary, depth, 'face', output )

	def getFromEdgeIndexes( self, edgeIndexes, edges, faceIndex ):
		"Initialize from edge indices."
		self.index = faceIndex
		self.edgeIndexes = edgeIndexes
		for edgeIndex in edgeIndexes:
			edges[ edgeIndex ].addFaceIndex( faceIndex )
		for triangleIndex in xrange( 3 ):
			indexFirst = ( 3 - triangleIndex ) % 3
			indexSecond = ( 4 - triangleIndex ) % 3
			self.vertexIndexes.append( getCommonVertexIndex( edges[ edgeIndexes[ indexFirst ] ], edges[ edgeIndexes[ indexSecond ] ] ) )
		return self

	def setEdgeIndexesToVertexIndexes( self, edges, edgeTable ):
		"Set the edge indexes to the vertex indexes."
		for triangleIndex in xrange( 3 ):
			indexFirst = ( 3 - triangleIndex ) % 3
			indexSecond = ( 4 - triangleIndex ) % 3
			vertexIndexFirst = self.vertexIndexes[ indexFirst ]
			vertexIndexSecond = self.vertexIndexes[ indexSecond ]
			vertexIndexPair = [ vertexIndexFirst, vertexIndexSecond ]
			vertexIndexPair.sort()
			edgeIndex = len( edges )
			if str( vertexIndexPair ) in edgeTable:
				edgeIndex = edgeTable[ str( vertexIndexPair ) ]
			else:
				edgeTable[ str( vertexIndexPair ) ] = edgeIndex
				edge = Edge().getFromVertexIndexes( edgeIndex, vertexIndexPair )
				edges.append( edge )
			edges[ edgeIndex ].addFaceIndex( self.index )
			self.edgeIndexes.append( edgeIndex )
		return self
