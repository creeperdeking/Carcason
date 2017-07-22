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
		self.player = player
		self.element = element

class Tile:
	def __init__(self, ID, elements=dict()):
		self.ID = ID
		self.rotation = int(0)

		self.elements = elements
		self.position = Position()

		self.pawns = []

	def addPawn(self, player, element):
		self.pawns.append(Pawn(player, element))

	def existElement(self, name, side):
		found = False
		genericName = name.split('_')[0]
		elementName = []
		for element in self.elements:
			if element.split('_')[0] == genericName:
				found = True
				elementName.append(element)

		if found:
			for i in elementName:
				if loopInt(side-self.rotation, 3) in self.elements[i]:
					return True
		return False

	def isCompatibleWith(self, side, tile):
		opposedSide = loopInt(side-2, 3)
		possibilities = []

		for rotation in range(0,4):
			for element in self.elements:
				if loopInt(side-rotation, 3) in self.elements[element]:
					if tile.existElement(element, opposedSide):
						possibilities.append(rotation)

		return possibilities

	def rotate(self):
		self.rotation = loopInt(self.rotation+1, 3)
