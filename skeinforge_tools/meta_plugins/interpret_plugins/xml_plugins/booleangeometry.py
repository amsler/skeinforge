"""
This page is in the table of contents.
The xml.py script is an import translator plugin to get a carving from an Art of Illusion xml file.

An import plugin is a script in the interpret_plugins folder which has the function getCarving.  It is meant to be run from the interpret tool.  To ensure that the plugin works on platforms which do not handle file capitalization properly, give the plugin a lower case name.

The getCarving function takes the file name of an xml file and returns the carving.

This example gets a triangle mesh for the xml file boolean.xml.  This example is run in a terminal in the folder which contains boolean.xml and xml.py.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import xml
>>> xml.getCarving().getCarveRotatedBoundaryLayers()
[-1.159765625, None, [[(-18.925000000000001-2.4550000000000001j), (-18.754999999999981-2.4550000000000001j)
..
many more lines of the carving
..


An xml file can be exported from Art of Illusion by going to the "File" menu, then going into the "Export" menu item, then picking the XML choice.  This will bring up the XML file chooser window, choose a place to save the file then click "OK".  Leave the "compressFile" checkbox unchecked.  All the objects from the scene will be exported, this plugin will ignore the light and camera.  If you want to fabricate more than one object at a time, you can have multiple objects in the Art of Illusion scene and they will all be carved, then fabricated together.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.fabmetheus_utilities.vector3 import Vector3
from skeinforge_tools.fabmetheus_utilities import boolean_carving
from skeinforge_tools.fabmetheus_utilities import euclidean
from skeinforge_tools.fabmetheus_utilities import triangle_mesh
import math

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addCarvableObjectWithMatrix( carvableObjects, matrix4X4, objectElement ):
	"Add the object info if it is carvable."
	carvableObject = getCarvableObject( objectElement )
	if carvableObject == None:
		return
	carvableObject.setShape( matrix4X4 )
	carvableObjects.append( carvableObject )

def getCarvableObject( objectElement ):
	"Get the object if it is carvable."
	if objectElement == None:
		return
	lowerClassName = objectElement.className.lower()
	if lowerClassName not in globalCarvableClassObjectTable:
		return
	if 'visible' in objectElement.attributeTable:
		if objectElement.attributeTable[ 'visible' ] == 'false':
			return
	carvableObject = globalCarvableClassObjectTable[ lowerClassName ]()
	if 'id' in objectElement.attributeTable:
		carvableObject.name = objectElement.attributeTable[ 'id' ]
	carvableObject.object = objectElement
	carvableObject.matrix4X4 = boolean_carving.Matrix4X4()
	matrixElement = objectElement.getFirstChildWithClassName( 'matrix4x4' )
	if matrixElement != None:
		carvableObject.matrix4X4.getFromAttributeTable( matrixElement.attributeTable )
	return carvableObject

def getCarvingFromParser( xmlParser ):
	"Get the carving for the parser."
	booleanGeometry = boolean_carving.BooleanGeometry()
	booleanGeometryElement = xmlParser.rootElement.getFirstChildWithClassName( 'booleangeometry' )
	objectElements = booleanGeometryElement.children
	for objectElement in objectElements:
		addCarvableObjectWithMatrix( booleanGeometry.carvableObjects, None, objectElement )
	return booleanGeometry


class BooleanSolid( boolean_carving.BooleanSolid ):
	"An Art of Illusion CSG object info."
	def setShape( self, matrix4X4 ):
		"Set the shape of this carvable object info."
		functionTable = { 'union': self.getUnion, 'intersection': self.getIntersection, 'firstminuscomplement': self.getFirstMinusComplement, 'lastminuscomplement': self.getLastMinusComplement }
		self.operationFunction = functionTable[ self.object.attributeTable[ 'operation' ] ]
		self.subObjects = []
		for objectElement in self.object.children:
			addCarvableObjectWithMatrix( self.subObjects, matrix4X4, objectElement )
		self.setShapeToObjectVariables( matrix4X4 )


class Cube( boolean_carving.Cube ):
	"An Art of Illusion Cube object."
	def setShape( self, matrix4X4 ):
		"Set the shape of this carvable object info."
		self.halfX = boolean_carving.getFloatOne( 'halfx', self.object.attributeTable )
		self.halfY = boolean_carving.getFloatOne( 'halfy', self.object.attributeTable )
		self.halfZ = boolean_carving.getFloatOne( 'halfz', self.object.attributeTable )
		self.setShapeToObjectVariables( matrix4X4 )


class Cylinder( boolean_carving.Cylinder ):
	"An Art of Illusion Cylinder object."
	def setShape( self, matrix4X4 ):
		"Set the shape of this carvable object info."
		self.height = boolean_carving.getFloatOne( 'height', self.object.attributeTable )
		self.radiusX = boolean_carving.getFloatOne( 'radiusx', self.object.attributeTable )
		self.topOverBottom = boolean_carving.getFloatOne( 'topoverbottom', self.object.attributeTable )
		self.radiusZ = boolean_carving.getFloatOne( 'radiusz', self.object.attributeTable )
		self.setShapeToObjectVariables( matrix4X4 )


class Sphere( boolean_carving.Sphere ):
	"An Art of Illusion Sphere object."
	def setShape( self, matrix4X4 ):
		"Set the shape of this carvable object."
		self.radiusX = boolean_carving.getFloatOne( 'radiusx', self.object.attributeTable )
		self.radiusY = boolean_carving.getFloatOne( 'radiusy', self.object.attributeTable )
		self.radiusZ = boolean_carving.getFloatOne( 'radiusz', self.object.attributeTable )
		self.setShapeToObjectVariables( matrix4X4 )


class TriangleMesh( boolean_carving.TriangleMesh ):
	"An Art of Illusion triangle mesh object."
	def setShape( self, matrix4X4 ):
		"Set the shape of this carvable object info."
		self.triangleMesh = triangle_mesh.TriangleMesh()
		verticesElement = self.object.getFirstChildWithClassName( 'vertices' )
		vector3Elements = verticesElement.getChildrenWithClassName( 'vector3' )
		for vector3Element in vector3Elements:
			vector3Table = vector3Element.attributeTable
			vertex = Vector3( boolean_carving.getFloatZero( 'x', vector3Table ), boolean_carving.getFloatZero( 'y', vector3Table ), boolean_carving.getFloatZero( 'z', vector3Table ) )
			self.triangleMesh.vertices.append( vertex )
		facesElement = self.object.getFirstChildWithClassName( 'faces' )
		faceElements = facesElement.getChildrenWithClassName( 'face' )
		for faceIndex in xrange( len( faceElements ) ):
			face = triangle_mesh.Face()
			faceElement = faceElements[ faceIndex ]
			face.index = faceIndex
			for vertexIndexIndex in xrange( 3 ):
				face.vertexIndexes.append( int( faceElement.attributeTable[ 'vertex' + str( vertexIndexIndex ) ] ) )
			self.triangleMesh.faces.append( face )
		self.triangleMesh.setEdgesForAllFaces()
		self.setShapeToObjectVariables( matrix4X4 )


globalCarvableClassObjectTable = { 'booleansolid' : BooleanSolid, 'cube' : Cube, 'cylinder' : Cylinder, 'sphere' : Sphere, 'trianglemesh' : TriangleMesh }
