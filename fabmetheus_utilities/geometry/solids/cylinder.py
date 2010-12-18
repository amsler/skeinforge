"""
Boolean geometry cylinder.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.manipulation_evaluator import matrix
from fabmetheus_utilities.geometry.solids import cube
from fabmetheus_utilities.geometry.solids import group
from fabmetheus_utilities.geometry.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math

__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


def addBeveledCylinder(bevel, endZ, inradius, outputs, start, topOverBottom, xmlElement):
	'Add beveled cylinder to outputs bevel, endZ, inradius and start.'
	height = abs(start.z - endZ)
	bevelStartRatio = max(1.0 - bevel / height, 0.5)
	oneMinusBevelStartRatio = 1.0 - bevelStartRatio
	trunkEndZ = bevelStartRatio * endZ + oneMinusBevelStartRatio * start.z
	trunkTopOverBottom = bevelStartRatio * topOverBottom + oneMinusBevelStartRatio
	outputs.append(getGeometryOutputByEndStart(trunkEndZ, inradius, start, trunkTopOverBottom, xmlElement))
	capInradius = inradius * trunkTopOverBottom
	capStart = bevelStartRatio * Vector3(start.x, start.y, endZ) + oneMinusBevelStartRatio * start
	inradiusMaximum = max(inradius.real, inradius.imag)
	endInradiusMaximum = inradiusMaximum * topOverBottom - bevel
	trunkInradiusMaximum = inradiusMaximum * trunkTopOverBottom
	capTopOverBottom = endInradiusMaximum / trunkInradiusMaximum
	outputs.append(getGeometryOutputByEndStart(endZ, capInradius, capStart, capTopOverBottom, xmlElement))

def addCylinderByInradius(faces, inradius, topOverBottom, vertexes, xmlElement):
	'Add cylinder by radius.'
	polygonBottom = []
	polygonTop = []
	sides = evaluate.getSidesMinimumThreeBasedOnPrecision(max(inradius.x, inradius.y), xmlElement )
	sideAngle = 2.0 * math.pi / sides
	for side in xrange(int(sides)):
		angle = float(side) * sideAngle
		unitComplex = euclidean.getWiddershinsUnitPolar(angle)
		pointBottom = complex(unitComplex.real * inradius.x, unitComplex.imag * inradius.y)
		polygonBottom.append(pointBottom)
		if topOverBottom > 0.0:
			polygonTop.append(pointBottom * topOverBottom)
	if topOverBottom <= 0.0:
		polygonTop.append(complex())
	bottomTopPolygon = [
		trianglemesh.getAddIndexedLoop(polygonBottom, vertexes, -inradius.z),
		trianglemesh.getAddIndexedLoop(polygonTop, vertexes, inradius.z)]
	trianglemesh.addPillarByLoops(faces, bottomTopPolygon)

def getGeometryOutput(inradius, topOverBottom, xmlElement):
	'Get cylinder triangle mesh by inradius.'
	faces = []
	vertexes = []
	addCylinderByInradius(faces, inradius, topOverBottom, vertexes, xmlElement)
	return {'trianglemesh' : {'vertex' : vertexes, 'face' : faces}}

def getGeometryOutputByEndStart(endZ, inradiusComplex, start, topOverBottom, xmlElement):
	'Get cylinder triangle mesh by endZ, inradius and start.'
	inradius = Vector3(inradiusComplex.real, inradiusComplex.imag, 0.5 * abs(endZ - start.z))
	cylinderOutput = getGeometryOutput(inradius, topOverBottom, xmlElement)
	vertexes = matrix.getVertexes(cylinderOutput)
	if endZ < start.z:
		for vertex in vertexes:
			vertex.z = -vertex.z
	translation = Vector3(start.x, start.y, inradius.z + min(start.z, endZ))
	euclidean.translateVector3Path(vertexes, translation)
	return cylinderOutput

def processXMLElement(xmlElement):
	'Process the xml element.'
	group.processShape( Cylinder, xmlElement)


class Cylinder( cube.Cube ):
	'A cylinder object.'
	def __init__(self):
		'Add empty lists.'
		self.radiusZ = None
		cube.Cube.__init__(self)

	def createShape(self):
		'Create the shape.'
		addCylinderByInradius(self.faces, self.inradius, self.topOverBottom, self.vertexes, self.xmlElement)

	def setToObjectAttributeDictionary(self):
		'Set the shape of this carvable object info.'
		self.inradius = evaluate.getVector3ByPrefixes(['demisize', 'inradius', 'radius'], Vector3(1.0, 1.0, 1.0), self.xmlElement)
		self.inradius = evaluate.getVector3ByMultiplierPrefixes(2.0, ['diameter', 'size'], self.inradius, self.xmlElement)
		self.inradius.z = 0.5 * evaluate.getEvaluatedFloatDefault(self.inradius.z + self.inradius.z, 'height', self.xmlElement)
		self.topOverBottom = evaluate.getEvaluatedFloatDefault(1.0, 'topOverBottom', self.xmlElement )
		self.xmlElement.attributeDictionary['height'] = self.inradius.z + self.inradius.z
		self.xmlElement.attributeDictionary['radius.x'] = self.inradius.x
		self.xmlElement.attributeDictionary['radius.y'] = self.inradius.y
		self.xmlElement.attributeDictionary['topOverBottom'] = self.topOverBottom
		self.createShape()
