"""
Copyright © <01/08/2017>, <Alexis Gros>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
Except as contained in this notice, the name of the <copyright holders> shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the <copyright holders>.
"""

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
