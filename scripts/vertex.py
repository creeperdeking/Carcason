"""
Copyright © <01/08/2017>, <Alexis Gros>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
Except as contained in this notice, the name of the <copyright holders> shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the <copyright holders>.
"""


from scripts.utils import *
from scripts.element_pawn import *

# A "vertice" is a part of the fields "meshs"
class Vertex:
	def __init__(self, position=Position(), tile=None, internVect=[0,0]):
		self.position = position
		self.tile = tile
		self.pawn = None

		self.internVect = internVect # Represent the position of the vertex inside the tile

		self.neighbors = [] # A vertex is connected with his surrounding vertice

	# If it is possible to put a pawn in this vertex:
	def canPutPawn(self):
		cp = 0
		for neighbor in self.neighbors:
			if neighbor[1] == "closed":
				cp+=1
		if cp == 4:
			return False
		return True

	# Finding the neighbors
	def buildLinks(self, verticeMap, map):
		self.neighbors = []
		nbCity = 0
		# We build link to the 4 sides of the vertex
		for side in range(0,4):
			vect = convertSideToVector(side)
			pos = Position([self.position.x+vect[0], self.position.y+vect[1]])

			city = None
			if not pos in verticeMap:
				isOpen = True
				for element in self.tile.elements:
					if element.name == "city":
						if convertVectorToSide(vect) in element.sides:
							isOpen = False
							city = element
				if isOpen:
					self.neighbors.append([Vertex(), "open", None, vect])
				else:
					self.neighbors.append([Vertex(), "closed", city, vect])
				continue

			# If the neighbors is inside our vertex's tile
			if verticeMap[pos].tile == verticeMap[self.position].tile:
				sideToCheck = 0
				if abs(vect[0]) == 1 and self.internVect[1] == 1:
					sideToCheck = 0
				elif abs(vect[0]) == 1 and self.internVect[1] == 0:
					sideToCheck = 2
				elif abs(vect[1]) == 1 and self.internVect[0] == 0:
					sideToCheck = 1
				elif abs(vect[1]) == 1 and self.internVect[0] == 1:
					sideToCheck = 3

				canLink = True
				for element in self.tile.elements:
					if element.name == "road":
						if sideToCheck in element.sides:
							canLink = False
					# We check special possibles city configuration:
					if element.name == "city":
						if sideToCheck in element.sides and loopInt(sideToCheck+2,3) in element.sides or sideToCheck in element.sides and loopInt(sideToCheck+1,3) in element.sides and loopInt(sideToCheck+3,3) in element.sides:
							canLink = False
							city = element
				if canLink:
					self.neighbors.append([verticeMap[pos], "linked", None, vect])
				else:
					self.neighbors.append([Vertex(), "closed", city, vect])
			else:
				canLink = True
				for element in self.tile.elements:
					if element.name == "city":
						if convertVectorToSide(vect) in element.sides:
							canLink = False
							city = element
				if canLink:
					self.neighbors.append([verticeMap[pos], "linked", None, vect])
				else:
					self.neighbors.append([Vertex(), "closed", city, vect])

	def __eq__(self, other):
		return (self.position) == (other.position)
