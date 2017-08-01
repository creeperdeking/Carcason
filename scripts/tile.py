"""
Copyright © <01/08/2017>, <Alexis Gros>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
Except as contained in this notice, the name of the <copyright holders> shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the <copyright holders>.
"""


import pdb
import math
import copy
import bge

from scripts.utils import *
from scripts.element_pawn import *
from scripts.vertex import *

# A class representing a Tile in the board:
class Tile:
	def __init__(self, ID, elements=list()):
		self.ID = ID
		self.rotation = 0

		self.elements = copy.deepcopy(elements)
		self.position = Position()

		self.pawns = []

		self.vertices = []

	def addPawn(self, player, element, value, obj):
		newPawn = Pawn(player, element, value)
		newPawn.obj = obj
		if element.sides[0] > 4:
			if self.vertices[element.sides[0]-5].canPutPawn():
				self.vertices[element.sides[0]-5].pawn = newPawn
			else:
				return False
		self.pawns.append(newPawn)
		return True

	def createVertice(self, verticeMap):
		verticePos = [[Position([self.position.x*2,self.position.y*2+1]), [0,1]],
						[Position([self.position.x*2,self.position.y*2]), [0,0]],
						[Position([self.position.x*2+1,self.position.y*2]), [1,0]],
						[Position([self.position.x*2+1,self.position.y*2+1]), [1,1]],
		]
		for v in verticePos:
			nVertex = Vertex(v[0],self, v[1])
			self.vertices.append(nVertex)
			verticeMap[v[0]] = nVertex

	def buildVertice(self, verticeMap, map):
		for v in self.vertices:
			v.buildLinks(verticeMap, map)

	# return the element with name and side
	def getElement(self, name, side):
		for element in self.elements:
			if element.name == name:
				if side in element.sides:
					return element
		return Element()

	# If name element with side exist
	def existElement(self, name, side):
		for element in self.elements:
			if element.name == name and side in element.sides:
				return True
		return False

	# Return the possible rotations were self can be beside the "side" side of the "tile" tile:
	def isCompatibleWith(self, side, tile):
		opposedSide = loopInt(side-2, 3)
		possibilities = []
		for rotation in range(0,4):
			for element in self.elements:
				if loopInt(side-rotation, 3) in element.sides:
					if tile.existElement(element.name, opposedSide):
						possibilities.append(rotation)

		return possibilities

	#Rotate the tile
	# if reinit, the
	def rotate(self, plus=1, reinit = False):
		if reinit:
			self.rotation = 0
		self.rotation = loopInt(self.rotation+plus, 3)
		for element in self.elements:
			if 4 in element.sides:
				continue
			newSides = []
			for side in element.sides:
				newSides.append(loopInt(side+plus, 3))
			element.sides = newSides
