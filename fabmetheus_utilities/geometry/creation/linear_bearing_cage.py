"""
Linear bearing cage.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import extrude
from fabmetheus_utilities.geometry.creation import lathe
from fabmetheus_utilities.geometry.creation import lineation
from fabmetheus_utilities.geometry.creation import solid
from fabmetheus_utilities.geometry.creation import teardrop
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.manipulation_evaluator import matrix
from fabmetheus_utilities.geometry.manipulation_evaluator import translate
from fabmetheus_utilities.geometry.solids import cylinder
from fabmetheus_utilities.geometry.solids import sphere
from fabmetheus_utilities.geometry.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = '$Date: 2008/02/05 $'
__license__ = 'GPL 3.0'


def addAssemblyCage(derivation, negatives, positives):
	'Add assembly linear bearing cage.'
	addCageGroove(derivation, negatives, positives)
	for pegCenterX in derivation.pegCenterXs:
		addPositivePeg(derivation, positives, pegCenterX, -derivation.pegY)
		addPositivePeg(derivation, positives, pegCenterX, derivation.pegY)
	translate.translateNegativesPositives(negatives, positives, Vector3(0.0, -derivation.halfSeparationWidth))
	femaleNegatives = []
	femalePositives = []
	addCageGroove(derivation, femaleNegatives, femalePositives)
	for pegCenterX in derivation.pegCenterXs:
		addNegativePeg(derivation, femaleNegatives, pegCenterX, -derivation.pegY)
		addNegativePeg(derivation, femaleNegatives, pegCenterX, derivation.pegY)
	translate.translateNegativesPositives(femaleNegatives, femalePositives, Vector3(0.0, derivation.halfSeparationWidth))
	negatives += femaleNegatives
	positives += femalePositives

def addCage(derivation, height, negatives, positives):
	'Add linear bearing cage.'
	copyShallow = derivation.xmlElement.getCopyShallow()
	copyShallow.attributeDictionary['path'] = [Vector3(), Vector3(0.0, 0.0, height)]
	extrudeDerivation = extrude.ExtrudeDerivation(copyShallow)
	roundedExtendedRectangle = getRoundedExtendedRectangle(derivation.demiwidth, derivation.rectangleCenterX, 14)
	outsidePath = euclidean.getVector3Path(roundedExtendedRectangle)
	extrude.addPositives(extrudeDerivation, [outsidePath], positives)
	for bearingCenterX in derivation.bearingCenterXs:
		addNegativeSphere(derivation, negatives, bearingCenterX)

def addCageGroove(derivation, negatives, positives):
	'Add cage and groove.'
	addCage(derivation, derivation.demiheight, negatives, positives)
	addGroove(derivation, negatives)

def addGroove(derivation, negatives):
	'Add groove on each side of cage.'
	copyShallow = derivation.xmlElement.getCopyShallow()
	extrude.setXMLElementToEndStart(Vector3(-derivation.demilength), Vector3(derivation.demilength), copyShallow)
	extrudeDerivation = extrude.ExtrudeDerivation(copyShallow)
	bottom = derivation.demiheight - 0.5 * derivation.grooveWidth
	outside = derivation.demiwidth
	top = derivation.demiheight
	leftGroove = [
		complex(-outside, bottom),
		complex(-derivation.innerDemiwidth, derivation.demiheight),
		complex(-outside, top)]
	rightGroove = [
		complex(outside, top),
		complex(derivation.innerDemiwidth, derivation.demiheight),
		complex(outside, bottom)]
	groovesComplex = [leftGroove, rightGroove]
	groovesVector3 = euclidean.getVector3Paths(groovesComplex)
	extrude.addPositives(extrudeDerivation, groovesVector3, negatives)

def addNegativePeg(derivation, negatives, x, y):
	'Add negative cylinder at x and y.'
	negativePegRadius = derivation.pegRadius + derivation.halfPegClearance
	inradius = complex(negativePegRadius, negativePegRadius)
	copyShallow = derivation.xmlElement.getCopyShallow()
	start = Vector3(x, y, derivation.height)
	cylinderOutput = cylinder.getGeometryOutputByEndStart(0.0, inradius, start, derivation.topOverBottom, copyShallow)
	negatives.append(cylinderOutput)

def addNegativeSphere(derivation, negatives, x):
	'Add negative sphere at x.'
	radius = Vector3(derivation.radiusPlusClearance, derivation.radiusPlusClearance, derivation.radiusPlusClearance)
	sphereOutput = sphere.getGeometryOutput(radius, derivation.xmlElement.getCopyShallow())
	euclidean.translateVector3Path(matrix.getVertexes(sphereOutput), Vector3(x, 0.0, derivation.demiheight))
	negatives.append(sphereOutput)

def addPositivePeg(derivation, positives, x, y):
	'Add positive cylinder at x and y.'
	positivePegRadius = derivation.pegRadius - derivation.halfPegClearance
	inradius = complex(positivePegRadius, positivePegRadius)
	copyShallow = derivation.xmlElement.getCopyShallow()
	start = Vector3(x, y, derivation.demiheight)
	endZ = derivation.height
	cylinder.addBeveledCylinder(derivation.pegBevel, endZ, inradius, positives, start, derivation.topOverBottom, copyShallow)

def getBearingCenterXs(bearingCenterX, numberOfSteps, stepX):
	'Get the bearing center x list.'
	bearingCenterXs = []
	for stepIndex in xrange(numberOfSteps + 1):
		bearingCenterXs.append(bearingCenterX)
		bearingCenterX += stepX
	return bearingCenterXs

def getPegCenterXs(numberOfSteps, pegCenterX, stepX):
	'Get the peg center x list.'
	pegCenterXs = []
	for stepIndex in xrange(numberOfSteps):
		pegCenterXs.append(pegCenterX)
		pegCenterX += stepX
	return pegCenterXs

def getGeometryOutput(derivation, xmlElement):
	'Get vector3 vertexes from attribute dictionary.'
	if derivation == None:
		derivation = LinearBearingCageDerivation(xmlElement)
	negatives = []
	positives = []
	if derivation.typeStringFirstCharacter == 'a':
		addAssemblyCage(derivation, negatives, positives)
	else:
		addCage(derivation, derivation.height, negatives, positives)
	return extrude.getGeometryOutputByNegativesPositivesOnly(negatives, positives, xmlElement)

def getGeometryOutputByArguments(arguments, xmlElement):
	'Get vector3 vertexes from attribute dictionary by arguments.'
	evaluate.setAttributeDictionaryByArguments(['length', 'radius'], arguments, xmlElement)
	return getGeometryOutput(None, xmlElement)

def getRoundedExtendedRectangle(radius, rectangleCenterX, sides):
	'Get the rounded extended rectangle.'
	roundedExtendedRectangle = []
	halfSides = int(sides / 2)
	halfSidesPlusOne = abs(halfSides + 1)
	sideAngle = math.pi / float(halfSides)
	extensionMultiplier = 1.0 / math.cos(0.5 * sideAngle)
	center = complex(rectangleCenterX, 0.0)
	startAngle = 0.5 * math.pi
	for halfSide in xrange(halfSidesPlusOne):
		unitPolar = euclidean.getWiddershinsUnitPolar(startAngle)
		unitPolarExtended = complex(unitPolar.real * extensionMultiplier, unitPolar.imag)
		roundedExtendedRectangle.append(unitPolarExtended * radius + center)
		startAngle += sideAngle
	center = complex(-rectangleCenterX, 0.0)
	startAngle = -0.5 * math.pi
	for halfSide in xrange(halfSidesPlusOne):
		unitPolar = euclidean.getWiddershinsUnitPolar(startAngle)
		unitPolarExtended = complex(unitPolar.real * extensionMultiplier, unitPolar.imag)
		roundedExtendedRectangle.append(unitPolarExtended * radius + center)
		startAngle += sideAngle
	return roundedExtendedRectangle

def processXMLElement(xmlElement):
	'Process the xml element.'
	solid.processXMLElementByGeometry(getGeometryOutput(None, xmlElement), xmlElement)


class LinearBearingCageDerivation:
	'Class to hold linear bearing cage variables.'
	def __init__(self, xmlElement):
		'Set defaults.'
		self.length = evaluate.getEvaluatedFloatDefault(50.0, 'length', xmlElement)
		self.demilength = 0.5 * self.length
		self.radius = lineation.getFloatByPrefixBeginEnd('radius', 'diameter', 5.0, xmlElement)
		self.cageClearanceOverRadius = evaluate.getEvaluatedFloatDefault(0.05, 'cageClearanceOverRadius', xmlElement)
		self.cageClearance = self.cageClearanceOverRadius * self.radius
		self.cageClearance = evaluate.getEvaluatedFloatDefault(self.cageClearance, 'cageClearance', xmlElement)
		self.racewayClearanceOverRadius = evaluate.getEvaluatedFloatDefault(0.1, 'racewayClearanceOverRadius', xmlElement)
		self.racewayClearance = self.racewayClearanceOverRadius * self.radius
		self.racewayClearance = evaluate.getEvaluatedFloatDefault(self.racewayClearance, 'racewayClearance', xmlElement)
		self.typeMenuRadioStrings = 'assembly integral'.split()
		self.typeString = evaluate.getEvaluatedStringDefault('assembly', 'type', xmlElement)
		self.typeStringFirstCharacter = self.typeString[: 1 ].lower()
		self.wallThicknessOverRadius = evaluate.getEvaluatedFloatDefault(0.5, 'wallThicknessOverRadius', xmlElement)
		self.wallThickness = self.wallThicknessOverRadius * self.radius
		self.wallThickness = evaluate.getEvaluatedFloatDefault(self.wallThickness, 'wallThickness', xmlElement)
		self.zenithAngle = evaluate.getEvaluatedFloatDefault(45.0, 'zenithAngle', xmlElement)
		self.zenithRadian = math.radians(self.zenithAngle)
		self.demiheight = self.radius * math.cos(self.zenithRadian) - self.racewayClearance
		self.height = self.demiheight + self.demiheight
		self.radiusPlusClearance = self.radius + self.cageClearance
		self.cageRadius = self.radiusPlusClearance + self.wallThickness
		self.demiwidth = self.cageRadius
		self.bearingCenterX = self.cageRadius - self.demilength
		separation = self.cageRadius + self.radiusPlusClearance
		bearingLength = -self.bearingCenterX - self.bearingCenterX
		self.numberOfSteps = int(math.floor(bearingLength / separation))
		self.stepX = bearingLength / float(self.numberOfSteps)
		self.bearingCenterXs = getBearingCenterXs(self.bearingCenterX, self.numberOfSteps, self.stepX)
		self.xmlElement = xmlElement
		if self.typeStringFirstCharacter == 'a':
			self.setAssemblyCage()
		self.rectangleCenterX = self.demiwidth - self.demilength

	def __repr__(self):
		'Get the string representation of this LinearBearingCageDerivation.'
		return str(self.__dict__)

	def setAssemblyCage(self):
		'Set two piece assembly parameters.'
		self.grooveDepthOverRadius = evaluate.getEvaluatedFloatDefault(0.15, 'grooveDepthOverRadius', self.xmlElement)
		self.grooveDepth = self.grooveDepthOverRadius * self.radius
		self.grooveDepth = evaluate.getEvaluatedFloatDefault(self.grooveDepth, 'grooveDepth', self.xmlElement)
		self.grooveWidthOverRadius = evaluate.getEvaluatedFloatDefault(0.6, 'grooveWidthOverRadius', self.xmlElement)
		self.grooveWidth = self.grooveWidthOverRadius * self.radius
		self.grooveWidth = evaluate.getEvaluatedFloatDefault(self.grooveWidth, 'grooveWidth', self.xmlElement)
		self.pegClearanceOverRadius = evaluate.getEvaluatedFloatDefault(0.0, 'pegClearanceOverRadius', self.xmlElement)
		self.pegClearance = self.pegClearanceOverRadius * self.radius
		self.pegClearance = evaluate.getEvaluatedFloatDefault(self.pegClearance, 'pegClearance', self.xmlElement)
		self.halfPegClearance = 0.5 * self.pegClearance
		self.pegRadiusOverRadius = evaluate.getEvaluatedFloatDefault(0.5, 'pegRadiusOverRadius', self.xmlElement)
		self.pegRadius = self.pegRadiusOverRadius * self.radius
		self.pegRadius = evaluate.getEvaluatedFloatDefault(self.pegRadius, 'pegRadius', self.xmlElement)
		self.pegBevelOverPegRadius = evaluate.getEvaluatedFloatDefault(0.25, 'pegBevelOverPegRadius', self.xmlElement)
		self.pegBevel = self.pegBevelOverPegRadius * self.pegRadius
		self.pegBevel = evaluate.getEvaluatedFloatDefault(self.pegBevel, 'pegBevel', self.xmlElement)
		self.pegMaximumRadius = self.pegRadius + abs(self.halfPegClearance)
		self.separationOverRadius = evaluate.getEvaluatedFloatDefault(0.5, 'separationOverRadius', self.xmlElement)
		self.separation = self.separationOverRadius * self.radius
		self.separation = evaluate.getEvaluatedFloatDefault(self.separation, 'separation', self.xmlElement)
		self.topOverBottom = evaluate.getEvaluatedFloatDefault(0.8, 'topOverBottom', self.xmlElement)
		self.quarterHeight = 0.5 * self.demiheight
		self.pegY = 0.5 * self.wallThickness + self.pegMaximumRadius
		cagePegRadius = self.cageRadius + self.pegMaximumRadius
		halfStepX = 0.5 * self.stepX
		pegHypotenuse = math.sqrt(self.pegY * self.pegY + halfStepX * halfStepX)
		if cagePegRadius > pegHypotenuse:
			self.pegY = math.sqrt(cagePegRadius * cagePegRadius - halfStepX * halfStepX)
		self.demiwidth = max(self.pegY + self.pegMaximumRadius + self.wallThickness, self.demiwidth)
		self.innerDemiwidth = self.demiwidth
		self.demiwidth += self.grooveDepth
		self.halfSeparationWidth = self.demiwidth + 0.5 * self.separation
		if self.pegRadius <= 0.0:
			self.pegCenterXs = []
		else:
			self.pegCenterXs = getPegCenterXs(self.numberOfSteps, self.bearingCenterX + halfStepX, self.stepX)
