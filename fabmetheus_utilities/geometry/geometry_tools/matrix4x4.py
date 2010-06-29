"""
Boolean geometry four by four matrix.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_utilities import evaluate
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

def getDiagonalSwitchedMatrix( angle, diagonals ):
	"Get the diagonals and switched matrix.math."
	unitPolar = euclidean.getWiddershinsUnitPolar( math.radians( angle ) )
	newMatrixTetragrid = getIdentityMatrixTetragrid()
	setDiagonalElements( diagonals, newMatrixTetragrid, unitPolar.real )
	newMatrixTetragrid[ diagonals[ 0 ] ][ diagonals[ 1 ] ] = - unitPolar.imag
	newMatrixTetragrid[ diagonals[ 1 ] ][ diagonals[ 0 ] ] = unitPolar.imag
	return Matrix4X4( newMatrixTetragrid )

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

def getTransformedVector3s( matrixTetragrid, vector3s ):
	"Get the vector3s multiplied by a matrix."
	transformedVector3s = []
	for vector3 in vector3s:
		transformedVector3 = getVector3TransformedByMatrix( matrixTetragrid, vector3 )
		transformedVector3s.append( transformedVector3 )
	return transformedVector3s

def getVector3TransformedByMatrix( matrixTetragrid, vector3 ):
	"Get the vector3 multiplied by a matrix."
	return Vector3(
		getTransformedByList( matrixTetragrid[ 0 ], vector3 ),
		getTransformedByList( matrixTetragrid[ 1 ], vector3 ),
		getTransformedByList( matrixTetragrid[ 2 ], vector3 ) )

def getZeroMatrixTetragrid():
	"Get four by four zero matrix."
	return [ [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ] ]

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	setXMLElementDictionaryToOtherElementDictionary( xmlElement, xmlElement.parent.object.matrix4X4, xmlElement.parent )

def setDiagonalElements( diagonals, matrixTetragrid, value ):
	"Set the diagonal matrix elements to the value."
	for diagonal in diagonals:
		matrixTetragrid[ diagonal ][ diagonal ] = value

def setAttributeDictionaryToMatrix( attributeDictionary, matrix4X4 ):
	"Set the attribute dictionary to the matrix."
	for row in xrange( 4 ):
		for column in xrange( 4 ):
			key = getMatrixKey( row, column )
			attributeDictionary[ key ] = str( matrix4X4.matrixTetragrid[ row ][ column ] )

def setAttributeDictionaryMatrixToMatrix( matrix4X4, xmlElement ):
	"Set the element attribute dictionary and element matrix to the matrix."
	setAttributeDictionaryToMatrix( xmlElement.attributeDictionary, matrix4X4 )
	if xmlElement.object != None:
		xmlElement.object.matrix4X4 = matrix4X4

def setMatrixTetragridToMatrixTetragrid( matrixTetragrid, otherMatrixTetragrid ):
	"Set the matrix grid to the other matirx grid."
	if otherMatrixTetragrid == None:
		return
	for row in xrange( 4 ):
		for column in xrange( 4 ):
			matrixTetragrid[ row ][ column ] = otherMatrixTetragrid[ row ][ column ]

def setXMLElementDictionaryToOtherElementDictionary( fromXMLElement, matrix4X4, xmlElement ):
	"Set the xml element to the matrix attribute dictionary."
	matrix4X4.getFromXMLElement( fromXMLElement )
	setAttributeDictionaryToMatrix( xmlElement.attributeDictionary, matrix4X4 )

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
		"Get the attributeDictionary from row column attribute strings, counting from one."
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

	def getFromMatrixValues( self, attributeDictionary ):
		"Get the values from row column attribute strings, counting from one."
		for row in xrange( 4 ):
			for column in xrange( 4 ):
				key = getMatrixKey( row, column )
				if key in attributeDictionary:
					value = attributeDictionary[ key ]
					if value == None or value == 'None':
						print( 'Warning, value in getFromMatrixValues in matrix4x4 is None for key for dictionary:' )
						print( key )
						print( attributeDictionary )
					else:
						self.matrixTetragrid[ row ][ column ] = float( value )
		return self

	def getFromXMLElement( self, xmlElement ):
		"Get the values from row column attribute strings, counting from one."
		attributeDictionary = xmlElement.attributeDictionary
		if attributeDictionary == None:
			return self
		self.multiplyByKeyFunction( xmlElement, 'scalex', getMatrixScaleX )
		self.multiplyByKeyFunction( xmlElement, 'scaley', getMatrixScaleY )
		self.multiplyByKeyFunction( xmlElement, 'scalez', getMatrixScaleZ )
		self.multiplyByKeysFunction( xmlElement, [ 'axisclockwisez', 'observerclockwisez', 'rotationz' ], getMatrixRotationZ )
		self.multiplyByKeysFunction( xmlElement, [ 'axiscounterclockwisez', 'observercounterclockwisez' ], getMatrixRotationZCounter )
		self.multiplyByKeysFunction( xmlElement, [ 'axisclockwisex', 'observerclockwisex', 'rotationx' ], getMatrixRotationX )
		self.multiplyByKeysFunction( xmlElement, [ 'axiscounterclockwisex', 'observercounterclockwisex' ], getMatrixRotationXCounter )
		self.multiplyByKeysFunction( xmlElement, [ 'axiscounterclockwisey', 'observerclockwisey', 'rotationy' ], getMatrixRotationY )
		self.multiplyByKeysFunction( xmlElement, [ 'axisclockwisey', 'observercounterclockwisey' ], getMatrixRotationYCounter )
		self.multiplyByKeyFunction( xmlElement, 'x', getMatrixTranslationX )
		self.multiplyByKeyFunction( xmlElement, 'y', getMatrixTranslationY )
		self.multiplyByKeyFunction( xmlElement, 'z', getMatrixTranslationZ )
		# http://en.wikipedia.org/wiki/Rotation_matrix zxy
		matrixKeys = getMatrixKeys()
		evaluatedDictionary = evaluate.getEvaluatedDictionary( matrixKeys, xmlElement )
		if len( evaluatedDictionary.keys() ) > 0:
			multiplicationMatrix4X4 = Matrix4X4().getFromMatrixValues( evaluatedDictionary )
			self.matrixTetragrid = self.getOtherTimesSelf( multiplicationMatrix4X4 ).matrixTetragrid
			euclidean.removeListFromDictionary( xmlElement.attributeDictionary, matrixKeys )
		return self

	def getIsDefault( self ):
		"Determine if this is the identity matrix."
		for row in xrange( 4 ):
			for column in xrange( 4 ):
				if float( column == row ) != self.matrixTetragrid[ row ][ column ]:
					return False
		return True

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

	def multiplyByKeyFunction( self, xmlElement, key, matrixFunction ):
		"Multiply matrix key, then delete the key."
		if key not in xmlElement.attributeDictionary:
			return
		floatValue = evaluate.getEvaluatedFloat( key, xmlElement )
		if floatValue == None:
			print( 'Warning, evaluated value in multiplyByKeyFunction in matrix4x4 is None for key:' )
			print( key )
			print( 'for xmlElement dictionary value:' )
			print( xmlElement.attributeDictionary[ key ] )
			print( 'for xmlElement dictionary:' )
			print( xmlElement.attributeDictionary )
			return
		multiplicationMatrix4X4 = matrixFunction( floatValue )
		self.matrixTetragrid = self.getOtherTimesSelf( multiplicationMatrix4X4 ).matrixTetragrid
		del xmlElement.attributeDictionary[ key ]

	def multiplyByKeysFunction( self, xmlElement, keys, matrixFunction ):
		"Multiply matrix keys, then delete the keys."
		for key in keys:
			self.multiplyByKeyFunction( xmlElement, key, matrixFunction )
