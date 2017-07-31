import pdb
import math
import copy

def convertSideToVector(side):
	sideVect = [0,0]
	if side == 0:
		sideVect = [0,1]
	elif side == 1:
		sideVect = [-1,0]
	elif side == 2:
		sideVect = [0,-1]
	elif side == 3:
		sideVect = [1,0]
	elif side == 4:
		sideVect = [0,0]
	elif side == 5:
		sideVect = [-1,1]
	elif side == 6:
		sideVect = [-1,-1]
	elif side == 7:
		sideVect = [1,-1]
	elif side == 8:
		sideVect = [1,1]
	return sideVect

def convertVectorToSide(vect):
	side = 4
	if vect == [0,1]:
		side = 0
	elif vect == [-1,0]:
		side = 1
	elif vect == [0,-1]:
		side = 2
	elif vect == [1,0]:
		side = 3
	return side

def loopInt(integrer, maxValue):
	if integrer > maxValue:
		return integrer - maxValue-1
	elif integrer < 0:
		return integrer + maxValue+1
	else:
		return integrer

class Position:
	def __init__(self, liste=[0,0]):
		self.x = int(liste[0])
		self.y = int(liste[1])

	def vect(self):
		return [self.x, self.y]

	def inv(self):
		return [loopInt(self.x+1,1), loopInt(self.y+1,1)]

	def __hash__(self):
		return hash((self.x, self.y))

	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)

class Pawn:
	def __init__(self, player, element, value=1):
		self.player = int(player)
		self.element = element

		self.value = value

class Element:
	def __init__(self, name="", sides=[], value=1):
		self.name = name
		self.sides = sides
		self.value = value

class Vertice:
	def __init__(self, position=Position(), tile=None, internVect=[0,0]):
		self.position = position
		self.tile = tile
		self.pawn = None

		self.internVect = internVect

		self.neighbors = []

	def buildLinks(self, verticeMap, map):
		self.neighbors = []
		nbCity = 0
		# We build link to the 4 sides of the vertice
		for side in range(0,4):
			vect = convertSideToVector(side)
			pos = Position([self.position.x+vect[0], self.position.y+vect[1]])
			if not pos in verticeMap:
				openeu = True
				for element in self.tile.elements:
					if element.name == "city":
						if convertVectorToSide(vect) in element.sides:
							openeu = False
				if openeu:
					self.neighbors.append([Vertice(), "open", vect])
				else:
					self.neighbors.append([Vertice(), "closed", vect])
				continue

			# If we are still inside the tile:
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
					if element.name == "city":
						if sideToCheck in element.sides and loopInt(sideToCheck+2,3) in element.sides:
							canLink = False
						if sideToCheck in element.sides and loopInt(sideToCheck+1,3) in element.sides and loopInt(sideToCheck+3,3) in element.sides:
							canLink = False
				if canLink:
					self.neighbors.append([verticeMap[pos], "linked", vect])
				else:
					self.neighbors.append([Vertice(), "closed", vect])
			else:
				canLink = True
				for element in self.tile.elements:
					if element.name == "city":
						if convertVectorToSide(vect) in element.sides:
							canLink = False
				if canLink:
					self.neighbors.append([verticeMap[pos], "linked", vect])
				else:
					self.neighbors.append([Vertice(), "closed", vect])

	def __eq__(self, other):
		return (self.position) == (other.position)


class Tile:
	def __init__(self, ID, elements=list()):
		self.ID = ID
		self.rotation = 0

		self.elements = copy.deepcopy(elements)
		self.position = Position()

		self.pawns = []

		self.vertices = []

	def addPawn(self, player, element, value):
		newPawn = Pawn(player, element, value)
		if element.sides[0] > 4:
			print(element.sides[0]-5)
			self.vertices[element.sides[0]-5].pawn = newPawn
		self.pawns.append(newPawn)

	def createVertice(self, verticeMap):
		verticePos = [[Position([self.position.x*2,self.position.y*2]), [0,0]],
						[Position([self.position.x*2,self.position.y*2+1]), [0,1]],
						[Position([self.position.x*2+1,self.position.y*2]), [1,0]],
						[Position([self.position.x*2+1,self.position.y*2+1]), [1,1]],
		]
		for v in verticePos:
			nVertice = Vertice(v[0],self, v[1])
			self.vertices.append(nVertice)
			verticeMap[v[0]] = nVertice

	def buildVertice(self, verticeMap, map):
		for v in self.vertices:
			v.buildLinks(verticeMap, map)

	def getElement(self, name, side):

		for element in self.elements:
			if element.name == name:
				if side in element.sides:
					return element
		return Element()

	def existElement(self, name, side):
		for element in self.elements:
			if element.name == name and side in element.sides:
				return True
		return False

	def isCompatibleWith(self, side, tile):
		opposedSide = loopInt(side-2, 3)
		possibilities = []
		for rotation in range(0,4):
			for element in self.elements:
				if loopInt(side-rotation, 3) in element.sides:
					if tile.existElement(element.name, opposedSide):
						possibilities.append(rotation)

		return possibilities

	def rotate(self, plus=1, reinit = False):
		if reinit:
			self.rotation = 0
		self.rotation = loopInt(self.rotation+plus, 3)
		for element in self.elements:
			if element.name == "abbey":
				continue
			newSides = []
			for side in element.sides:
				newSides.append(loopInt(side+plus, 3))
			element.sides = newSides

class Player:
	def __init__(self, name):
		self.name = name
		self.nbPawns = 7
		self.nbBigPawns = 1

		self.score = 0
