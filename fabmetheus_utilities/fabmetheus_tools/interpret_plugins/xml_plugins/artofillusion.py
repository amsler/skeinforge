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

from fabmetheus_utilities.shapes.solid_tools import face
from fabmetheus_utilities.shapes.solid_tools import matrix4x4
from fabmetheus_utilities.shapes.solid_utilities import boolean_carving
from fabmetheus_utilities.shapes.solid_utilities import booleansolid
from fabmetheus_utilities.shapes.solid_utilities import solid
from fabmetheus_utilities.shapes import cube
from fabmetheus_utilities.shapes import cylinder
from fabmetheus_utilities.shapes import group
from fabmetheus_utilities.shapes import sphere
from fabmetheus_utilities.shapes import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCarvingFromParser( xmlParser ):
	"Get the carving for the parser."
	booleanGeometry = boolean_carving.BooleanGeometry()
	artOfIllusionElement = xmlParser.getRootElement()
	euclidean.removeListFromDictionary( artOfIllusionElement.attributeDictionary, [ 'fileversion', 'xmlns:bf' ] )
	sceneElement = artOfIllusionElement.getFirstChildWithClassName( 'Scene' )
	xmlElements = sceneElement.getFirstChildWithClassName( 'objects' ).getChildrenWithClassName( 'bf:Elem' )
	for xmlElement in xmlElements:
		processXMLElement( booleanGeometry.archivableObjects, xmlElement )
	return booleanGeometry

def getCarvableObject( globalObject, object, xmlElement ):
	"Get new carvable object info."
	archivableObject = globalObject()
	archivableObject.xmlElement = object
	object.attributeDictionary[ 'id' ] = xmlElement.getFirstChildWithClassName( 'name' ).text
	object.object = archivableObject
	coords = xmlElement.getFirstChildWithClassName( 'coords' )
	transformXMLElement = getTransformXMLElement( coords, 'transformFrom' )
	if len( transformXMLElement.attributeDictionary ) < 16:
		transformXMLElement = getTransformXMLElement( coords, 'transformTo' )
	matrix4x4.setXMLElementMatrixToMatrixAttributeDictionary( transformXMLElement, object.object.matrix4X4, object )
	return archivableObject

def getTransformXMLElement( coords, transformName ):
	"Get the transform attributes."
	transformXMLElement = coords.getFirstChildWithClassName( transformName )
	if len( transformXMLElement.attributeDictionary ) < 16:
		if 'bf:ref' in transformXMLElement.attributeDictionary:
			idReference = transformXMLElement.attributeDictionary[ 'bf:ref' ]
			return coords.getRootElement().getSubChildWithID( idReference )
	return transformXMLElement

def processXMLElement( archivableObjects, xmlElement ):
	"Add the object info if it is carvable."
	if xmlElement == None:
		return
	object = xmlElement.getFirstChildWithClassName( 'object' )
	if 'bf:type' not in object.attributeDictionary:
		return
	shapeType = object.attributeDictionary[ 'bf:type' ]
	if shapeType not in globalCarvableClassObjectTable:
		return
	carvableClassObject = globalCarvableClassObjectTable[ shapeType ]
	archivableObject = getCarvableObject( carvableClassObject, object, xmlElement )
	archivableObject.xmlElement.attributeDictionary[ 'visible' ] = xmlElement.attributeDictionary[ 'visible' ]
	archivableObject.setToObjectAttributeDictionary()
	archivableObjects.append( archivableObject )

def removeListArtOfIllusionFromDictionary( dictionary, scrubKeys ):
	"Remove the list and art of illusion keys from the dictionary."
	euclidean.removeListFromDictionary( dictionary, [ 'bf:id', 'bf:type' ] )
	euclidean.removeListFromDictionary( dictionary, scrubKeys )


class BooleanSolid( booleansolid.BooleanSolid ):
	"An Art of Illusion CSG object info."
	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		functionTable = { '0': self.getUnion, '1': self.getIntersection, '2': self.getDifference, '3': self.reverseArchivableObjects }
		self.operationFunction = functionTable[ self.xmlElement.attributeDictionary[ 'operation' ] ]
		processXMLElement( self.archivableObjects, self.xmlElement.getFirstChildWithClassName( 'obj1' ) )
		processXMLElement( self.archivableObjects, self.xmlElement.getFirstChildWithClassName( 'obj2' ) )
		removeListArtOfIllusionFromDictionary( self.xmlElement.attributeDictionary, [ 'operation' ] )


class Cube( cube.Cube ):
	"An Art of Illusion Cube object."
	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		self.halfX = float( self.xmlElement.attributeDictionary[ 'halfx' ] )
		self.halfY = float( self.xmlElement.attributeDictionary[ 'halfy' ] )
		self.halfZ = float( self.xmlElement.attributeDictionary[ 'halfz' ] )
		removeListArtOfIllusionFromDictionary( self.xmlElement.attributeDictionary, [] )
		self.createShape()


class Cylinder( cylinder.Cylinder ):
	"An Art of Illusion Cylinder object."
	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		self.height = float( self.xmlElement.attributeDictionary[ 'height' ] )
		self.radiusX = float( self.xmlElement.attributeDictionary[ 'rx' ] )
		self.radiusZ = float( self.xmlElement.attributeDictionary[ 'rz' ] )
		self.topOverBottom = float( self.xmlElement.attributeDictionary[ 'ratio' ] )
		self.xmlElement.attributeDictionary[ 'radiusx' ] = self.xmlElement.attributeDictionary[ 'rx' ]
		self.xmlElement.attributeDictionary[ 'radiusz' ] = self.xmlElement.attributeDictionary[ 'rz' ]
		self.xmlElement.attributeDictionary[ 'topoverbottom' ] = self.xmlElement.attributeDictionary[ 'ratio' ]
		removeListArtOfIllusionFromDictionary( self.xmlElement.attributeDictionary, [ 'rx', 'rz', 'ratio' ] )
		self.createShape()


class Group( group.Group ):
	"An Art of Illusion Group object."
	def setToObjectAttributeDictionary( self ):
		"Set the shape of this group."
		childrenElement = self.xmlElement.parent.getFirstChildWithClassName( 'children' )
		children = childrenElement.getChildrenWithClassName( 'bf:Elem' )
		for child in children:
			processXMLElement( self.archivableObjects, child )
		removeListArtOfIllusionFromDictionary( self.xmlElement.attributeDictionary, [] )


class Sphere( sphere.Sphere ):
	"An Art of Illusion Sphere object."
	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object."
		self.radiusX = float( self.xmlElement.attributeDictionary[ 'rx' ] )
		self.radiusY = float( self.xmlElement.attributeDictionary[ 'ry' ] )
		self.radiusZ = float( self.xmlElement.attributeDictionary[ 'rz' ] )
		self.xmlElement.attributeDictionary[ 'radiusx' ] = self.xmlElement.attributeDictionary[ 'rx' ]
		self.xmlElement.attributeDictionary[ 'radiusy' ] = self.xmlElement.attributeDictionary[ 'ry' ]
		self.xmlElement.attributeDictionary[ 'radiusz' ] = self.xmlElement.attributeDictionary[ 'rz' ]
		removeListArtOfIllusionFromDictionary( self.xmlElement.attributeDictionary, [ 'rx', 'ry', 'rz' ] )
		self.createShape()


class TriangleMesh( trianglemesh.TriangleMesh ):
	"An Art of Illusion triangle mesh object."
	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		vertexElement = self.xmlElement.getFirstChildWithClassName( 'vertex' )
		vertexPointElements = vertexElement.getChildrenWithClassName( 'bf:Elem' )
		for vertexPointElement in vertexPointElements:
			coordinateElement = vertexPointElement.getFirstChildWithClassName( 'r' )
			vertex = Vector3( float( coordinateElement.attributeDictionary[ 'x' ] ), float( coordinateElement.attributeDictionary[ 'y' ] ), float( coordinateElement.attributeDictionary[ 'z' ] ) )
			self.vertices.append( vertex )
		edgeElement = self.xmlElement.getFirstChildWithClassName( 'edge' )
		edgeSubelements = edgeElement.getChildrenWithClassName( 'bf:Elem' )
		for edgeSubelementIndex in xrange( len( edgeSubelements ) ):
			edgeSubelement = edgeSubelements[ edgeSubelementIndex ]
			vertexIndexes = [ int( edgeSubelement.attributeDictionary[ 'v1' ] ), int( edgeSubelement.attributeDictionary[ 'v2' ] ) ]
			edge = face.Edge().getFromVertexIndexes( edgeSubelementIndex, vertexIndexes )
			self.edges.append( edge )
		faceElement = self.xmlElement.getFirstChildWithClassName( 'face' )
		faceSubelements = faceElement.getChildrenWithClassName( 'bf:Elem' )
		for faceSubelementIndex in xrange( len( faceSubelements ) ):
			faceSubelement = faceSubelements[ faceSubelementIndex ]
			edgeIndexes = [ int( faceSubelement.attributeDictionary[ 'e1' ] ), int( faceSubelement.attributeDictionary[ 'e2' ] ), int( faceSubelement.attributeDictionary[ 'e3' ] ) ]
			self.faces.append( face.Face().getFromEdgeIndexes( edgeIndexes, self.edges, faceSubelementIndex ) )
		removeListArtOfIllusionFromDictionary( self.xmlElement.attributeDictionary, [ 'closed', 'smoothingMethod' ] )


globalCarvableClassObjectTable = { 'CSGObject' : BooleanSolid, 'Cube' : Cube, 'Cylinder' : Cylinder, 'artofillusion.object.NullObject' : Group, 'Sphere' : Sphere, 'TriangleMesh' : TriangleMesh }
