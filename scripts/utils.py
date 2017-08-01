# A simple class to represent a 2D position:
class Position:
	def __init__(self, liste=[0,0]):
		self.x = int(liste[0])
		self.y = int(liste[1])

	def vect(self):
		return [self.x, self.y]

	def __hash__(self):
		return hash((self.x, self.y))

	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)

# A function to loop between 0 and maxValue:
def loopInt(integrer, maxValue):
	if integrer > maxValue:
		return integrer - maxValue-1
	elif integrer < 0:
		return integrer + maxValue+1
	else:
		return integrer

# Convert the side into a vector that represent the orientation of the side from the center of the tile:
def convertSideToVector(side):
	#Important: 8 possible sides:
	#  ____________
	# |     0      |
	# |  5      8  |
	# |1    4     3|
	# |  6      7  |
	# |_____2______|

	sideVect = [0,0]
	if side == 0:
		sideVect = [0,1]
	elif side == 1:
		sideVect = [-1,0]
	elif side == 2:
		sideVect = [0,-1]
	elif side == 3:
		sideVect = [1,0]
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
	if vect == [-1,1]:
		side = 5
	elif vect == [-1,-1]:
		side = 6
	elif vect == [1,-1]:
		side = 7
	elif vect == [1,1]:
		side = 8
	return side
