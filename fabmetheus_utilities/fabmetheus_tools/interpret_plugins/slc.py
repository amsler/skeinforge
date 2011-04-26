"""
This page is in the table of contents.
The slc.py script is an import translator plugin to get a carving from an slc file.

An import plugin is a script in the interpret_plugins folder which has the function getCarving.  It is meant to be run from the interpret tool.  To ensure that the plugin works on platforms which do not handle file capitalization properly, give the plugin a lower case name.

The getCarving function takes the file name of an slc file and returns the carving.

This example gets a triangle mesh for the slc file rotor.slc.  This example is run in a terminal in the folder which contains rotor.slc and slc.py.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import slc
>>> slc.getCarving()
0.20000000298, 999999999.0, -999999999.0, [8.72782748851e-17, None
..
many more lines of the carving
..


An explanation of the SLC format can be found at:
http://rapid.lpt.fi/archives/rp-ml-1999/0713.html

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import svg_writer
from struct import unpack
import math
import sys


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


def getCarving(fileName=''):
	"Get the triangle mesh for the slc file."
	carving = SLCCarving()
	carving.readFile(fileName)
	return carving

def getLittleEndianFloatGivenFile( file ):
	"Get little endian float given a file."
	return unpack('<f', file.read(4) )[0]

def getLittleEndianUnsignedLongGivenFile( file ):
	"Get little endian float given a file."
	return unpack('<L', file.read(4) )[0]

def getPointsFromFile( numPoints, file ):
	"Process the vertice points for a given boundary."
	points = []
	for pointIndex in xrange( numPoints ):
		x = getLittleEndianFloatGivenFile( file )
		y = getLittleEndianFloatGivenFile( file )
		points.append( complex(x, y) )
	return points

def readHeader( file ):
	"Read the slc header."
	while ord( file.read( 1 ) ) != 0x1A:
		pass


class SampleTableEntry:
	"Sample table entry."
	def __init__( self, file ):
		"Read in the sampling table section. It contains a table length (byte) and the table entries."
		self.min_z_level = getLittleEndianFloatGivenFile( file )
		self.layer_thickness = getLittleEndianFloatGivenFile( file )
		self.beam_comp = getLittleEndianFloatGivenFile( file )
		getLittleEndianFloatGivenFile( file )

	def __repr__(self):
		"Get the string representation of this sample table entry."
		return '%s, %s, %s' % ( self.min_z_level, self.layer_thickness, self.beam_comp )


class SLCCarving:
	"An slc carving."
	def __init__(self):
		"Add empty lists."
		self.maximumZ = - 999999999.0
		self.minimumZ = 999999999.0
		self.layerThickness = None
		self.rotatedLoopLayers = []
	
	def __repr__(self):
		"Get the string representation of this carving."
		return self.getCarvedSVG()

	def addXML(self, depth, output):
		"Add xml for this object."
		xml_simple_writer.addXMLFromObjects(depth, self.rotatedLoopLayers, output)

	def getCarveCornerMaximum(self):
		"Get the corner maximum of the vertexes."
		return self.cornerMaximum

	def getCarveCornerMinimum(self):
		"Get the corner minimum of the vertexes."
		return self.cornerMinimum

	def getCarvedSVG(self):
		"Get the carved svg text."
		if len(self.rotatedLoopLayers) < 1:
			return ''
		decimalPlaces = max(0, 2 - int(math.floor(math.log10(self.layerThickness))))
		self.svgWriter = svg_writer.SVGWriter(True, self.cornerMaximum, self.cornerMinimum, decimalPlaces, self.layerThickness)
		return self.svgWriter.getReplacedSVGTemplate(self.fileName, 'basic', self.rotatedLoopLayers)

	def getCarveLayerThickness(self):
		"Get the layer thickness."
		return self.layerThickness

	def getCarveRotatedBoundaryLayers(self):
		"Get the rotated boundary layers."
		return self.rotatedLoopLayers

	def getFabmetheusXML(self):
		"Return the fabmetheus XML."
		return None

	def getInterpretationSuffix(self):
		"Return the suffix for a carving."
		return 'svg'

	def processContourLayers( self, file ):
		"Process a contour layer at a time until the top of the part."
		while True:
			minLayer = getLittleEndianFloatGivenFile( file )
			numContours = getLittleEndianUnsignedLongGivenFile( file )
			if numContours == 0xFFFFFFFF:
				return
			rotatedLoopLayer = euclidean.RotatedLoopLayer( minLayer )
			self.rotatedLoopLayers.append( rotatedLoopLayer )
			for contourIndex in xrange( numContours ):
				numPoints = getLittleEndianUnsignedLongGivenFile( file )
				numGaps = getLittleEndianUnsignedLongGivenFile( file )
				if numPoints > 2:
					rotatedLoopLayer.loops.append( getPointsFromFile( numPoints, file ) )

	def readFile( self, fileName ):
		"Read SLC and store the layers."
		self.fileName = fileName
		pslcfile = open( fileName, 'rb')
		readHeader( pslcfile )
		pslcfile.read( 256 ) #Go past the 256 byte 3D Reserved Section.
		self.readTableEntry( pslcfile )
		self.processContourLayers( pslcfile )
		pslcfile.close()
		self.cornerMaximum = Vector3(-999999999.0, -999999999.0, self.maximumZ)
		self.cornerMinimum = Vector3(999999999.0, 999999999.0, self.minimumZ)
		for rotatedLoopLayer in self.rotatedLoopLayers:
			for loop in rotatedLoopLayer.loops:
				for point in loop:
					pointVector3 = Vector3(point.real, point.imag, rotatedLoopLayer.z)
					self.cornerMaximum.maximize(pointVector3)
					self.cornerMinimum.minimize(pointVector3)
		halfLayerThickness = 0.5 * self.layerThickness
		self.cornerMaximum.z += halfLayerThickness
		self.cornerMinimum.z -= halfLayerThickness

	def readTableEntry( self, file ):
		"Read in the sampling table section. It contains a table length (byte) and the table entries."
		tableEntrySize = ord( file.read( 1 ) )
		if tableEntrySize == 0:
			print( "Sampling table size is zero!" )
			exit()
		for index in xrange( tableEntrySize ):
			sampleTableEntry = SampleTableEntry( file )
			self.layerThickness = sampleTableEntry.layer_thickness

	def setCarveBridgeLayerThickness( self, bridgeLayerThickness ):
		"Set the bridge layer thickness.  If the infill is not in the direction of the bridge, the bridge layer thickness should be given as None or not set at all."
		pass

	def setCarveLayerThickness( self, layerThickness ):
		"Set the layer thickness."
		pass

	def setCarveImportRadius( self, importRadius ):
		"Set the import radius."
		pass

	def setCarveIsCorrectMesh( self, isCorrectMesh ):
		"Set the is correct mesh flag."
		pass


def main():
	"Display the inset dialog."
	if len(sys.argv) > 1:
		getCarving(' '.join(sys.argv[1 :]))

if __name__ == "__main__":
	main()
