"""
Svg_writer is a class and collection of utilities to read from and write to an svg file.

Svg_writer uses the layer_template.svg file in the templates folder in the same folder as svg_writer, to output an svg file.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities.xml_simple_reader import XMLElement
from fabmetheus_utilities.xml_simple_reader import XMLSimpleReader
from fabmetheus_utilities import archive
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import xml_simple_writer
import cStringIO
import math
import os


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = '$Date: 2008/02/05 $'
__license__ = 'GPL 3.0'


def getCarving(fileName):
	'Get a carving for the file using an import plugin.'
	pluginModule = fabmetheus_interpret.getInterpretPlugin(fileName)
	if pluginModule == None:
		return None
	return pluginModule.getCarving(fileName)

def getSliceDictionary(xmlElement):
	'Get the metadata slice attribute dictionary.'
	for metadataElement in xmlElement.getChildrenWithClassName('metadata'):
		for child in metadataElement.children:
			if child.className.lower() == 'slice:layers':
				return child.attributeDictionary
	return {}

def getSliceXMLElements(xmlElement):
	'Get the slice elements.'
	gXMLElements = xmlElement.getChildrenWithClassNameRecursively('g')
	sliceXMLElements = []
	for gXMLElement in gXMLElements:
		if 'id' in gXMLElement.attributeDictionary:
			idValue = gXMLElement.attributeDictionary['id'].strip()
			if idValue.startswith('z:'):
				sliceXMLElements.append(gXMLElement)
	return sliceXMLElements

def getSVGByLoopLayers(addLayerTemplateToSVG, rotatedLoopLayers, svgCarving):
	'Get the svg text.'
	if len(rotatedLoopLayers) < 1:
		return ''
	decimalPlacesCarried = max(0, 2 - int(math.floor(math.log10(svgCarving.layerThickness))))
	svgWriter = SVGWriter(addLayerTemplateToSVG, svgCarving, decimalPlacesCarried)
	return svgWriter.getReplacedSVGTemplate(svgCarving.fileName, 'basic', rotatedLoopLayers, svgCarving.getFabmetheusXML())

def getTruncatedRotatedBoundaryLayers( repository, rotatedBoundaryLayers ):
	'Get the truncated rotated boundary layers.'
	return rotatedBoundaryLayers[ repository.layersFrom.value : repository.layersTo.value ]

def setSVGCarvingCorners(rotatedLoopLayers, svgCarving):
	'Parse SVG text and store the layers.'
	for rotatedBoundaryLayer in rotatedLoopLayers:
		for loop in rotatedBoundaryLayer.loops:
			for point in loop:
				pointVector3 = Vector3(point.real, point.imag, rotatedBoundaryLayer.z)
				svgCarving.cornerMaximum = euclidean.getPointMaximum(svgCarving.cornerMaximum, pointVector3)
				svgCarving.cornerMinimum = euclidean.getPointMinimum(svgCarving.cornerMinimum, pointVector3)


class SVGWriter:
	'A base class to get an svg skein from a carving.'
	def __init__(self, addLayerTemplateToSVG, carving, decimalPlacesCarried, perimeterWidth = None):
		self.addLayerTemplateToSVG = addLayerTemplateToSVG
		self.carving = carving
		self.decimalPlacesCarried = decimalPlacesCarried
		self.perimeterWidth = perimeterWidth
		self.textHeight = 22.5
		self.unitScale = 3.7

	def addLayerBegin(self, layerIndex, rotatedBoundaryLayer):
		'Add the start lines for the layer.'
		zRounded = self.getRounded( rotatedBoundaryLayer.z )
		self.graphicsCopy = self.graphicsXMLElement.getCopy(zRounded, self.graphicsXMLElement.parent)
		if self.addLayerTemplateToSVG:
			translateXRounded = self.getRounded(self.controlBoxWidth + self.margin + self.margin)
			layerTranslateY = self.marginTop
			layerTranslateY += layerIndex * self.textHeight + (layerIndex + 1) * (self.extent.y * self.unitScale + self.margin)
			translateYRounded = self.getRounded(layerTranslateY)
			self.graphicsCopy.attributeDictionary['transform'] = 'translate(%s, %s)' % (translateXRounded, translateYRounded)
			layerString = 'Layer %s, z:%s' % (layerIndex, zRounded)
			self.graphicsCopy.getFirstChildWithClassName('text').text = layerString
			self.graphicsCopy.attributeDictionary['inkscape:groupmode'] = 'layer'
			self.graphicsCopy.attributeDictionary['inkscape:label'] = layerString
		self.pathXMLElement = self.graphicsCopy.getFirstChildWithClassName('path')
		self.pathDictionary = self.pathXMLElement.attributeDictionary

	def addOriginalAsComment(self, xmlElement):
		'Add original xmlElement as a comment.'
		if xmlElement == None:
			return
		commentElement = XMLElement()
		commentElement.className = 'comment'
		xmlElementOutput = cStringIO.StringIO()
		xmlElement.addXML(0, xmlElementOutput)
		textLines = archive.getTextLines(xmlElementOutput.getvalue())
		commentElementOutput = cStringIO.StringIO()
		isComment = False
		for textLine in textLines:
			lineStripped = textLine.strip()
			if lineStripped[: len('<!--')] == '<!--':
				isComment = True
			if not isComment:
				if len(textLine) > 0:
					commentElementOutput.write(textLine + '\n')
			if '-->' in lineStripped:
				isComment = False
		commentElement.text = '<!-- Original XML Text:\n%s-->\n' % commentElementOutput.getvalue()
		commentElement.setParentAddToChildren(self.svgElement)

	def addRotatedLoopLayerToOutput( self, layerIndex, rotatedBoundaryLayer ):
		'Add rotated boundary layer to the output.'
		self.addLayerBegin( layerIndex, rotatedBoundaryLayer )
		if rotatedBoundaryLayer.rotation != None:
			self.graphicsCopy.attributeDictionary['bridgeRotation'] = str( rotatedBoundaryLayer.rotation )
		if self.addLayerTemplateToSVG:
			self.pathDictionary['transform'] = self.getTransformString()
		else:
			del self.pathDictionary['transform']
		self.pathDictionary['d'] = self.getSVGStringForLoops(rotatedBoundaryLayer.loops)

	def addRotatedLoopLayersToOutput( self, rotatedBoundaryLayers ):
		'Add rotated boundary layers to the output.'
		for rotatedBoundaryLayerIndex, rotatedBoundaryLayer in enumerate( rotatedBoundaryLayers ):
			self.addRotatedLoopLayerToOutput( rotatedBoundaryLayerIndex, rotatedBoundaryLayer )

	def getReplacedSVGTemplate(self, fileName, procedureName, rotatedBoundaryLayers, xmlElement=None):
		'Get the lines of text from the layer_template.svg file.'
		cornerMaximum = self.carving.getCarveCornerMaximum()
		cornerMinimum = self.carving.getCarveCornerMinimum()
		self.extent = cornerMaximum - cornerMinimum
		svgTemplateText = archive.getFileTextInFileDirectory( __file__, os.path.join('templates', 'layer_template.svg') )
		self.xmlParser = XMLSimpleReader( fileName, None, svgTemplateText )
		self.svgElement = self.xmlParser.getRoot()
		svgElementDictionary = self.svgElement.attributeDictionary
		self.sliceDictionary = getSliceDictionary(self.svgElement)
		self.controlBoxHeight = float(self.sliceDictionary['controlBoxHeight'])
		self.controlBoxWidth = float(self.sliceDictionary['controlBoxWidth'])
		self.margin = float(self.sliceDictionary['margin'])
		self.marginTop = float(self.sliceDictionary['marginTop'])
		svgMinWidth = float(self.sliceDictionary['svgMinWidth'])
		self.controlBoxHeightMargin = self.controlBoxHeight + self.marginTop
		if not self.addLayerTemplateToSVG:
			self.svgElement.getXMLElementByID('layerTextTemplate').removeFromIDNameParent()
			del self.svgElement.getXMLElementByID('sliceElementTemplate').attributeDictionary['transform']
		self.graphicsXMLElement = self.svgElement.getXMLElementByID('sliceElementTemplate')
		self.graphicsXMLElement.attributeDictionary['id'] = 'z:'
		self.addRotatedLoopLayersToOutput(rotatedBoundaryLayers)
		self.setMetadataNoscriptElement('layerThickness', 'Layer Thickness: ', self.carving.getCarveLayerThickness() )
		self.setMetadataNoscriptElement('maxX', 'X: ', cornerMaximum.x)
		self.setMetadataNoscriptElement('minX', 'X: ', cornerMinimum.x)
		self.setMetadataNoscriptElement('maxY', 'Y: ', cornerMaximum.y)
		self.setMetadataNoscriptElement('minY', 'Y: ', cornerMinimum.y)
		self.setMetadataNoscriptElement('maxZ', 'Z: ', cornerMaximum.z)
		self.setMetadataNoscriptElement('minZ', 'Z: ', cornerMinimum.z)
		self.textHeight = float( self.sliceDictionary['textHeight'] )
		controlTop = len(rotatedBoundaryLayers) * (self.margin + self.extent.y * self.unitScale + self.textHeight) + self.marginTop + self.textHeight
		self.svgElement.getFirstChildWithClassName('title').text = os.path.basename(fileName) + ' - Slice Layers'
		svgElementDictionary['height'] = '%spx' % self.getRounded(max(controlTop, self.controlBoxHeightMargin))
		width = max(self.extent.x * self.unitScale, svgMinWidth)
		svgElementDictionary['width'] = '%spx' % self.getRounded( width )
		self.sliceDictionary['decimalPlacesCarried'] = str( self.decimalPlacesCarried )
		if self.perimeterWidth != None:
			self.sliceDictionary['perimeterWidth'] = self.getRounded( self.perimeterWidth )
		self.sliceDictionary['yAxisPointingUpward'] = 'true'
		self.sliceDictionary['procedureDone'] = procedureName
		self.setDimensionTexts('dimX', 'X: ' + self.getRounded(self.extent.x))
		self.setDimensionTexts('dimY', 'Y: ' + self.getRounded(self.extent.y))
		self.setDimensionTexts('dimZ', 'Z: ' + self.getRounded(self.extent.z))
		self.setTexts('numberOfLayers', 'Number of Layers: %s' % len(rotatedBoundaryLayers))
		volume = 0.0
		for rotatedBoundaryLayer in rotatedBoundaryLayers:
			volume += euclidean.getAreaLoops(rotatedBoundaryLayer.loops)
		volume *= 0.001
		self.setTexts('volume', 'Volume: %s cm3' % self.getRounded(volume))
		if not self.addLayerTemplateToSVG:
			self.svgElement.getFirstChildWithClassName('script').removeFromIDNameParent()
			self.svgElement.getXMLElementByID('isoControlBox').removeFromIDNameParent()
			self.svgElement.getXMLElementByID('layerControlBox').removeFromIDNameParent()
			self.svgElement.getXMLElementByID('scrollControlBox').removeFromIDNameParent()
		self.graphicsXMLElement.removeFromIDNameParent()
		self.addOriginalAsComment(xmlElement)
		output = cStringIO.StringIO()
		output.write(self.xmlParser.beforeRoot)
		self.svgElement.addXML(0, output)
		return xml_simple_writer.getBeforeRootOutput(self.xmlParser)

	def getRounded(self, number):
		'Get number rounded to the number of carried decimal places as a string.'
		return euclidean.getRoundedToPlacesString(self.decimalPlacesCarried, number)

	def getRoundedComplexString(self, point):
		'Get the rounded complex string.'
		return self.getRounded( point.real ) + ' ' + self.getRounded( point.imag )

	def getSVGStringForLoop( self, loop ):
		'Get the svg loop string.'
		if len(loop) < 1:
			return ''
		return self.getSVGStringForPath(loop) + ' z'

	def getSVGStringForLoops( self, loops ):
		'Get the svg loops string.'
		loopString = ''
		if len(loops) > 0:
			loopString += self.getSVGStringForLoop( loops[0] )
		for loop in loops[1 :]:
			loopString += ' ' + self.getSVGStringForLoop(loop)
		return loopString

	def getSVGStringForPath( self, path ):
		'Get the svg path string.'
		svgLoopString = ''
		for point in path:
			stringBeginning = 'M '
			if len( svgLoopString ) > 0:
				stringBeginning = ' L '
			svgLoopString += stringBeginning + self.getRoundedComplexString(point)
		return svgLoopString

	def setMetadataNoscriptElement(self, key, prefix, value):
		'Set the metadata value and the text.'
		valueString = self.getRounded(value)
		self.sliceDictionary[key] = valueString
		self.setDimensionTexts(key, prefix + valueString)

	def setDimensionTexts(self, key, valueString):
		'Set the texts to the valueString followed by mm.'
		self.setTexts(key, valueString + ' mm')

	def setTexts(self, key, valueString):
		'Set the texts to the valueString.'
		self.svgElement.getXMLElementByID(key + 'Iso').text = valueString
		self.svgElement.getXMLElementByID(key + 'Layer').text = valueString
		self.svgElement.getXMLElementByID(key + 'Scroll').text = valueString

	def getTransformString(self):
		'Get the svg transform string.'
		cornerMinimumXString = self.getRounded(-self.carving.getCarveCornerMinimum().x)
		cornerMinimumYString = self.getRounded(-self.carving.getCarveCornerMinimum().y)
		return 'scale(%s, %s) translate(%s, %s)' % (self.unitScale, - self.unitScale, cornerMinimumXString, cornerMinimumYString)
