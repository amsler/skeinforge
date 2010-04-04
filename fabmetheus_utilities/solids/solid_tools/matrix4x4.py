"""
Boolean geometry four by four matrix.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import xml_simple_writer
import cStringIO
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getAngleFromDictionaryKey( dictionary, key ):
	"Get the angle from the dictionary and key."
	return math.radians( float( dictionary[ key ] ) )

def getIdentityMatrixTetragrid():
	"Get four by four matrix with diagonal elements set to one."
	identityMatrix = getZeroMatrixTetragrid()
	setDiagonalElements( range( 4 ), identityMatrix, 1.0 )
	return identityMatrix

def getMatrixKey( row, column ):
	"Get the key string from row & column, counting from one."
	return 'm' + str( row + 1 ) + str( column + 1 )

def getMatrixKeys():
	"Get the matrix keys."
	matrixKeys = []
	for row in xrange( 4 ):
		for column in xrange( 4 ):
			key = getMatrixKey( row, column )
			matrixKeys.append( key )
	return matrixKeys

def getMatrixRotationX( angle ):
	"Get matrix from the rotation x value."
	return getDiagonalSwitchedMatrix( - angle, [ 1, 2 ] )

def getMatrixRotationXCounter( angle ):
	"Get matrix from the rotation counter x value."
	return getDiagonalSwitchedMatrix( angle, [ 1, 2 ] )

def getMatrixRotationY( angle ):
	"Get matrix from the rotation y value."
	return getDiagonalSwitchedMatrix( angle, [ 0, 2 ] )

def getMatrixRotationYCounter( angle ):
	"Get matrix from the rotation counter y value."
	return getDiagonalSwitchedMatrix( - angle, [ 0, 2 ] )

def getMatrixRotationZ( angle ):
	"Get matrix from the rotation z value."
	return getDiagonalSwitchedMatrix( - angle, [ 0, 1 ] )

def getMatrixRotationZCounter( angle ):
	"Get matrix from the rotation counter z value."
	return getDiagonalSwitchedMatrix( angle, [ 0, 1 ] )

def getMatrixScaleX( scaleX ):
	"Get matrix from the scale x value."
	return Matrix4X4().getFromMatrixValues( { 'm11' : str( scaleX ) } )

def getMatrixScaleY( scaleY ):
	"Get matrix from the scale y value."
	return Matrix4X4().getFromMatrixValues( { 'm22' : str( scaleY ) } )

def getMatrixScaleZ( scaleZ ):
	"Get matrix from the scale z value."
	return Matrix4X4().getFromMatrixValues( { 'm33' : str( scaleZ ) } )

def getMatrixTranslationX( x ):
	"Get matrix from the translation x value."
	return Matrix4X4().getFromMatrixValues( { 'm14' : str( x ) } )

def getMatrixTranslationY( y ):
	"Get matrix from the translation y value."
	return Matrix4X4().getFromMatrixValues( { 'm24' : str( y ) } )

def getMatrixTranslationZ( z ):
	"Get matrix from the translation z value."
	return Matrix4X4().getFromMatrixValues( { 'm34' : str( z ) } )

def getMultipliedMatrixTetragrid( matrixTetragrid, otherMatrixTetragrid ):
	"Get this matrix multiplied by the other matrix."
	#A down, B right from http://en.wikipedia.org/wiki/Matrix_multiplication
	multipliedMatrixTetragrid = getZeroMatrixTetragrid()
	for row in xrange( 4 ):
		matrixRow = matrixTetragrid[ row ]
		for column in xrange( 4 ):
			dotProduct = 0
			for elementIndex in xrange( 4 ):
				dotProduct += matrixRow[ elementIndex ] * otherMatrixTetragrid[ elementIndex ][ column ]
			multipliedMatrixTetragrid[ row ][ column ] = dotProduct
	return multipliedMatrixTetragrid

def getTransformedByList( floatList, point ):
	"Get the point transformed by the array."
	return floatList[ 0 ] * point.x + floatList[ 1 ] * point.y + floatList[ 2 ] * point.z + floatList[ 3 ]

def getVector3TransformedByMatrix( matrixTetragrid, vector3 ):
	"Get the vector3 multiplied by a matrix."
	vector3Transformed = Vector3()
	vector3Transformed.x = getTransformedByList( matrixTetragrid[ 0 ], vector3 )
	vector3Transformed.y = getTransformedByList( matrixTetragrid[ 1 ], vector3 )
	vector3Transformed.z = getTransformedByList( matrixTetragrid[ 2 ], vector3 )
	return vector3Transformed

def getZeroMatrixTetragrid():
	"Get four by four zero matrix."
	return [ [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ] ]

def processXMLElement( xmlElement ):
	"Process the xml element."
	setXMLElementToMatrixAttributeDictionary( xmlElement.attributeDictionary, xmlElement.parent )

def setDiagonalElements( diagonals, matrixTetragrid, value ):
	"Set the diagonal matrix elements to the value."
	for diagonal in diagonals:
		matrixTetragrid[ diagonal ][ diagonal ] = value

def getDiagonalSwitchedMatrix( angle, diagonals ):
	"Get the diagonals and switched matrix.math."
	unitPolar = euclidean.getWiddershinsUnitPolar( math.radians( angle ) )
	newMatrixTetragrid = getIdentityMatrixTetragrid()
	setDiagonalElements( diagonals, newMatrixTetragrid, unitPolar.real )
	newMatrixTetragrid[ diagonals[ 0 ] ][ diagonals[ 1 ] ] = - unitPolar.imag
	newMatrixTetragrid[ diagonals[ 1 ] ][ diagonals[ 0 ] ] = unitPolar.imag
	return Matrix4X4( newMatrixTetragrid )

def setMatrixTetragridToMatrixTetragrid( matrixTetragrid, otherMatrixTetragrid ):
	"Set the matrix grid to the other matirx grid."
	if otherMatrixTetragrid == None:
		return
	for row in xrange( 4 ):
		for column in xrange( 4 ):
			matrixTetragrid[ row ][ column ] = otherMatrixTetragrid[ row ][ column ]

def setXMLElementToMatrixAttributeDictionary( attributeDictionary, xmlElement ):
	"Set the xml element to the matrix attribute dictionary."
	xmlElement.object.matrix4X4.getFromAttributeDictionary( attributeDictionary )
	for row in xrange( 4 ):
		for column in xrange( 4 ):
			key = getMatrixKey( row, column )
			xmlElement.attributeDictionary[ key ] = str( xmlElement.object.matrix4X4.matrixTetragrid[ row ][ column ] )

def transformVector3ByMatrix( matrixTetragrid, vector3 ):
	"Transform the vector3 by a matrix."
	vector3.setToVector3( getVector3TransformedByMatrix( matrixTetragrid, vector3 ) )


class Matrix4X4:
	"A four by four matrix."
	def __init__( self, matrixTetragrid = None ):
		"Add empty lists."
		self.matrixTetragrid = getIdentityMatrixTetragrid()
		setMatrixTetragridToMatrixTetragrid( self.matrixTetragrid, matrixTetragrid )

	def __repr__( self ):
		"Get the string representation of this four by four matrix."
		output = cStringIO.StringIO()
		self.addXML( 0, output )
		return output.getvalue()

	def addXML( self, depth, output ):
		"Add xml for this object."
		attributeDictionary = self.getAttributeDictionary()
		if len( attributeDictionary ) > 0:
			xml_simple_writer.addClosedXMLTag( attributeDictionary, depth, self.__class__.__name__.lower(), output )

	def getAttributeDictionary( self ):
		"Get the from row column attribute strings, counting from one."
		attributeDictionary = {}
		for row in xrange( 4 ):
			for column in xrange( 4 ):
				default = float( column == row )
				value = self.matrixTetragrid[ row ][ column ]
				if abs( value - default ) > 0.00000000000001:
					if abs( value ) < 0.00000000000001:
						value = 0.0
					attributeDictionary[ getMatrixKey( row, column ) ] = value
		return attributeDictionary

	def getFromAttributeDictionary( self, attributeDictionary ):
		"Get the values from row column attribute strings, counting from one."
		if attributeDictionary == None:
			return self
		self.multiplyByKeyFunction( attributeDictionary, 'scalex', getMatrixScaleX )
		self.multiplyByKeyFunction( attributeDictionary, 'scaley', getMatrixScaleY )
		self.multiplyByKeyFunction( attributeDictionary, 'scalez', getMatrixScaleZ )
		self.multiplyByKeysFunction( attributeDictionary, [ 'axisclockwisez', 'observerclockwisez', 'rotationz' ], getMatrixRotationZ )
		self.multiplyByKeysFunction( attributeDictionary, [ 'axiscounterclockwisez', 'observercounterclockwisez' ], getMatrixRotationZCounter )
		self.multiplyByKeysFunction( attributeDictionary, [ 'axisclockwisex', 'observerclockwisex', 'rotationx' ], getMatrixRotationX )
		self.multiplyByKeysFunction( attributeDictionary, [ 'axiscounterclockwisex', 'observercounterclockwisex' ], getMatrixRotationXCounter )
		self.multiplyByKeysFunction( attributeDictionary, [ 'axiscounterclockwisey', 'observerclockwisey', 'rotationy' ], getMatrixRotationY )
		self.multiplyByKeysFunction( attributeDictionary, [ 'axisclockwisey', 'observercounterclockwisey' ], getMatrixRotationYCounter )
		self.multiplyByKeyFunction( attributeDictionary, 'x', getMatrixTranslationX )
		self.multiplyByKeyFunction( attributeDictionary, 'y', getMatrixTranslationY )
		self.multiplyByKeyFunction( attributeDictionary, 'z', getMatrixTranslationZ )
		# http://en.wikipedia.org/wiki/Rotation_matrix zxy
		self.getFromMatrixValues( attributeDictionary )
		euclidean.removeListFromDictionary( attributeDictionary, getMatrixKeys() )
		return self

	def getFromMatrixValues( self, attributeDictionary ):
		"Get the values from row column attribute strings, counting from one."
		for row in xrange( 4 ):
			for column in xrange( 4 ):
				key = getMatrixKey( row, column )
				if key in attributeDictionary:
					self.matrixTetragrid[ row ][ column ] = float( attributeDictionary[ key ] )
		return self

	def getOtherTimesSelf( self, otherMatrix4X4 ):
		"Get this matrix reverse multiplied by the other matrix."
		if otherMatrix4X4 == None:
			return Matrix4X4( self.matrixTetragrid )
		return otherMatrix4X4.getSelfTimesOther( self.matrixTetragrid )

	def getSelfTimesOther( self, otherMatrixTetragrid ):
		"Get this matrix multiplied by the other matrix."
		if otherMatrixTetragrid == None:
			return Matrix4X4( self.matrixTetragrid )
		if self.matrixTetragrid == None:
			return None
		return Matrix4X4( getMultipliedMatrixTetragrid( self.matrixTetragrid, otherMatrixTetragrid ) )

	def multiplyByKeyFunction( self, attributeDictionary, key, matrixFunction ):
		"Multiply matrix key, then delete the key."
		if key not in attributeDictionary:
			return
		floatValue = float( attributeDictionary[ key ] )
		multiplicationMatrix4X4 = matrixFunction( floatValue )
		self.matrixTetragrid = self.getOtherTimesSelf( multiplicationMatrix4X4 ).matrixTetragrid
		del attributeDictionary[ key ]

	def multiplyByKeysFunction( self, attributeDictionary, keys, matrixFunction ):
		"Multiply matrix keys, then delete the keys."
		for key in keys:
			self.multiplyByKeyFunction( attributeDictionary, key, matrixFunction )
