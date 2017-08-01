# Represent an element of a tile:
class Element:
	def __init__(self, name="", sides=[], value=1):
		self.name = name
		self.sides = sides
		self.value = value # The number of points gained when completing this element

# Represent a Pawn:
class Pawn:
	def __init__(self, player, element, value=1):
		self.player = int(player)
		self.element = element
		self.obj = None

		self.value = value # The importance of the pawn (1 = 1 pawn, 2 = 2 pawns)

class Player:
	def __init__(self, name):
		self.name = name
		self.nbPawns = 7
		self.nbBigPawns = 1

		self.score = 0
