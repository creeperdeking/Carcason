import pdb

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

	def __hash__(self):
		return hash((self.x, self.y))

	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)

class Pawn:
	def __init__(self, player, element):
		self.player = int(player)
		self.element = element

class Element:
	def __init__(self, name="", sides=[], value=1):
		self.name = name
		self.sides = sides
		self.value = value

class Tile:
	def __init__(self, ID, elements=list()):
		self.ID = ID
		self.rotation = 0

		self.elements = elements
		self.position = Position()

		self.pawns = []

	def addPawn(self, player, element):
		self.pawns.append(Pawn(player, element))

	def getElement(self, name, side):
		for element in self.elements:
			if element.name == name:
				if side == 4 or loopInt(side-self.rotation, 3) in element.sides:
					return element
		return Element()

	def existElement(self, name, side):
		for element in self.elements:
			if element.name == name and loopInt(side-self.rotation, 3) in element.sides:
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

	def rotate(self, plus=1):
		self.rotation = loopInt(self.rotation+plus, 3)

class Player:
	def __init__(self, name):
		self.name = name
		self.nbPawns = 7
		self.nbBigPawns = 1

		self.score = 0
