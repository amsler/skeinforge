"""
This page is in the table of contents.
The py.py script is an import plugin to get a carving from a skeinforge python procedural script, in order to make procedural objects.

This is similar in concept, although different in execution, to the Masked Retriever's parametric scripts at:
http://blog.thingiverse.com/2009/10/20/parametric-objects-again/
http://blog.thingiverse.com/2009/10/19/parametric-object-party-day-1-the-power-of-standard-custom/

An example procedural script is circular_wave.py in the model folder.

An import plugin is a script in the interpret_plugins folder which has the function getCarving.  It is meant to be run from the interpret tool.  To ensure that the plugin works on platforms which do not handle file capitalization properly, give the plugin a lower case name.  The getCarving function takes the file name of a python script and returns the carving.

This example gets a carving for the python script circular_wave.py.  This example is run in a terminal in the folder which contains circular_wave.py and py.py.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import py
>>> py.getCarving()
0.20000000298, 999999999.0, -999999999.0, [8.72782748851e-17, None
..
many more lines of the carving
..


"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
import os
import sys

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCarving( fileName = ''):
	"Get the triangle mesh for the slc file."
	return PythonCarving( fileName )


class PythonCarving:
	"A python carving."
	def __init__( self, fileName ):
		"Add empty lists."
		self.maximumZ = - 999999999.0
		self.minimumZ = 999999999.0
		self.layerThickness = None
		self.rotatedBoundaryLayers = []
		self.untilDotName = gcodec.getUntilDot( fileName )
	
	def __repr__( self ):
		"Get the string representation of this carving."
		return '%s, %s, %s, %s' % ( self.layerThickness, self.minimumZ, self.maximumZ, self.rotatedBoundaryLayers )

	def getCarveCornerMaximum( self ):
		"Get the corner maximum of the vertices."
		return self.cornerMaximum

	def getCarveCornerMinimum( self ):
		"Get the corner minimum of the vertices."
		return self.cornerMinimum

	def getCarveLayerThickness( self ):
		"Get the layer thickness."
		return self.layerThickness

	def getCarveRotatedBoundaryLayers( self ):
		"Get the rotated boundary layers."
		self.importModule()
		self.cornerMaximum = Vector3( - 999999999.0, - 999999999.0, self.maximumZ )
		self.cornerMinimum = Vector3( 999999999.0, 999999999.0, self.minimumZ )
		for rotatedBoundaryLayer in self.rotatedBoundaryLayers:
			for loop in rotatedBoundaryLayer.loops:
				for point in loop:
					pointVector3 = Vector3( point.real, point.imag, rotatedBoundaryLayer.z )
					self.cornerMaximum = euclidean.getPointMaximum( self.cornerMaximum, pointVector3 )
					self.cornerMinimum = euclidean.getPointMinimum( self.cornerMinimum, pointVector3 )
		halfLayerThickness = 0.5 * self.layerThickness
		self.cornerMaximum.z += halfLayerThickness
		self.cornerMinimum.z -= halfLayerThickness
		return self.rotatedBoundaryLayers

	def importModule( self ):
		"Import the python script and store the layers."
		path = os.path.abspath( self.untilDotName )
		pluginModule = gcodec.getModuleWithPath( path )
		loopLayers = pluginModule.getLoopLayers( self.layerThickness )
		for loopLayer in loopLayers:
			rotatedBoundaryLayer = euclidean.RotatedLoopLayer( loopLayer.z )
			rotatedBoundaryLayer.loops = loopLayer.loops
			self.rotatedBoundaryLayers.append( rotatedBoundaryLayer )

	def setCarveBridgeLayerThickness( self, bridgeLayerThickness ):
		"Set the bridge layer thickness.  If the infill is not in the direction of the bridge, the bridge layer thickness should be given as None or not set at all."
		pass

	def setCarveLayerThickness( self, layerThickness ):
		"Set the layer thickness."
		self.layerThickness = layerThickness

	def setCarveImportRadius( self, importRadius ):
		"Set the import radius."
		pass

	def setCarveIsCorrectMesh( self, isCorrectMesh ):
		"Set the is correct mesh flag."
		pass


def main():
	"Display the inset dialog."
	if len( sys.argv ) > 1:
		getCarving(' '.join( sys.argv[ 1 : ] ) )

if __name__ == "__main__":
	main()
