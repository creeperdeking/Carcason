"""
Copyright © <01/08/2017>, <Alexis Gros>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
Except as contained in this notice, the name of the <copyright holders> shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the <copyright holders>.
"""


from scripts.utils import *
from scripts.tile import *

import bge
import bge.logic as logic
import bge.events as events

class CarcaMap:
	def __init__(self, game):
		self.game = game

		self.map = dict()

		self.possiblePos = [] # Store the possible position that the currentTile can take
		self.possiblePosFlags = [] # Store the objects added to show possiblePos
		self.verticeFlags = []

		self.verticeMap = dict() #Store the vertices by position, like self.map.map

		self.showLinks = 0

		self.scene = logic.getCurrentScene()

	def loadMapFromFile(self, filePath, defaultStackPath):
		self.map = dict()

		configFile = open(filePath, "r")
		fileContent = configFile.read()
		fileTable = fileContent.split("\n")

		self.game.currentPlayer = int(fileTable[0])
		del fileTable[0]

		step = 0
		for cptr,line in enumerate(fileTable):
			if line == '':
				continue
			if line == ';':
				step+=1
				continue

			words = line.split(' ')
			#First step, setup the players:
			if step == 0:
				player = Player(words[0])
				player.nbPawns = int(words[1])
				player.nbGreatPawn = int(words[2])
				player.score = int(words[3])
				self.game.players.append(player)
			#Second step, setup the map
			elif step == 1:
				position = Position(words[0].split(','))
				tile = self.game.addTile(words[1], position, int(words[2]))

				for v in range(0,3):
					del words[0]

				for j in words:
					pawnCarac = j.split(':')
					element= None
					if int(pawnCarac[2]) > 4:
						element = Element("field", [int(pawnCarac[2])])
					else:
						element = tile.getElement(pawnCarac[1], int(pawnCarac[2]))
					self.game.addPawn(position, element, int(pawnCarac[3]), int(pawnCarac[0]))

			#Third step, setup the tile stack:
			else:
				self.game.tileStack = list(words)
				break

		if self.game.tileStack[0] == "none":
			defaultStackFile = open(defaultStackPath, "r")
			fileContent = defaultStackFile.read()
			fileTab = fileContent.split('\n')[0].split(' ')
			random.shuffle(fileTab)
			self.game.tileStack = fileTab
		self.updateVerticeLinks()
		configFile.close()

	def saveMap(self, filePath):
		configFile = open(filePath, "w")
		configFile.write(str(self.game.currentPlayer)+"\n")
		for player in self.game.players:
			configFile.write(" ".join([player.name,str(player.nbPawns),str(player.nbBigPawns), str(player.score)])+"\n")
		configFile.write(";\n")

		for key in self.map:
			tile = self.map[key]
			pawnsString = " "

			for pawn in tile[0].pawns:
				side = pawn.element.sides[0]
				pawnsString += str(pawn.player)+":"+pawn.element.name+":"+str(side)+":"+str(pawn.value)+" "
			pawnsString = pawnsString[:-1]
			configFile.write(str(key.x)+","+str(key.y)+" "+tile[0].ID+" "+str(tile[0].rotation)+pawnsString+"\n")
		configFile.write(";\n")

		for cptr,tileID in enumerate(self.game.tileStack):
			configFile.write(tileID)
			if cptr != len(self.game.tileStack)-1:
				configFile.write(" ")
		configFile.close()

	def findPossiblePos(self):
		self.possiblePos = []

		for key in self.map:
			#First, create the list of the surrounding positions of the tile:
			pp = []
			for i in self.possiblePos:
				pp.append(i[0])
			if not Position([key.x, key.y+1]) in self.map:
				if not Position([key.x, key.y+1]) in pp:
					self.possiblePos.append([Position([key.x, key.y+1]), []])
			if not Position([key.x+1, key.y]) in self.map:
				if not Position([key.x+1, key.y]) in pp:
					self.possiblePos.append([Position([key.x+1, key.y]), []])
			if not Position([key.x, key.y-1]) in self.map:
				if not Position([key.x, key.y-1]) in pp:
					self.possiblePos.append([Position([key.x, key.y-1]), []])
			if not Position([key.x-1, key.y]) in self.map:
				if not Position([key.x-1, key.y]) in pp:
					self.possiblePos.append([Position([key.x-1, key.y]), []])

			badPos = []
			for cptr,posPos in enumerate(self.possiblePos):
				goodSides = []
				# Get, for each side of the possible position, the list of compatible rotations:
				possibilities = []
				if Position([posPos[0].x, posPos[0].y+1]) in self.map:
					possibilities.append(self.game.currentTile.isCompatibleWith(0, self.map[Position([posPos[0].x, posPos[0].y+1])][0]))
				if Position([posPos[0].x+1, posPos[0].y]) in self.map:
					possibilities.append(self.game.currentTile.isCompatibleWith(3, self.map[Position([posPos[0].x+1, posPos[0].y])][0]))
				if Position([posPos[0].x, posPos[0].y-1]) in self.map:
					possibilities.append(self.game.currentTile.isCompatibleWith(2, self.map[Position([posPos[0].x, posPos[0].y-1])][0]))
				if Position([posPos[0].x-1, posPos[0].y]) in self.map:
					possibilities.append(self.game.currentTile.isCompatibleWith(1, self.map[Position([posPos[0].x-1, posPos[0].y])][0]))
				# Test if a rotation is common to all side:
				nbBadSide = 0
				for side in range(0,4):
					ok = True
					for possibility in possibilities:
						if not (side in possibility):
							ok = False
					if not ok:
						nbBadSide+=1
					else:
						goodSides.append(side)
				posPos[1] = goodSides
				if nbBadSide == 4:
					badPos.append(cptr)

			badPos = sorted(badPos)
			for i in range(0,len(badPos)):
				del self.possiblePos[badPos[len(badPos)-1-i]]
		if not self.possiblePos:
			return False
		return True

	def showPossiblePos(self):
		self.hidePossiblePos()
		for position in self.possiblePos:
			obj = self.scene.addObject("tileFlag.blue")
			obj.position[0] = position[0].x
			obj.position[1] = position[0].y
			self.possiblePosFlags.append(obj)

	def hidePossiblePos(self):
		for obj in self.possiblePosFlags:
			obj.endObject()
		self.possiblePosFlags = []

	def updateVerticeLinks(self):
		for tile in self.map.values():
			tile[0].buildVertice(self.verticeMap, self.map)
		if self.showLinks:
			self.hideVerticeLinks()
			self.showVerticeLinks()
		else:
			self.hideVerticeLinks()

	def showVerticeLinks(self):
		for vertex in self.verticeMap.values():
			tile = vertex.tile
			for neighbor in vertex.neighbors:
				pos = [tile.position.x - 0.5 + vertex.internVect[0]/2 +.25 + neighbor[3][0]/8,
						tile.position.y - 0.5 + vertex.internVect[1]/2 +.25 + neighbor[3][1]/8,
						1]
				obj = self.scene.addObject("line.black")
				if neighbor[1] == "closed":
					if neighbor[2]:
						obj = self.scene.addObject("line.red")
				elif neighbor[1] == "linked":
					obj = self.scene.addObject("line.green")
				elif neighbor[1] == "open":
						obj = self.scene.addObject("line.white")
				obj.position = pos
				if abs(neighbor[3][1]) == 1:
					a = obj.orientation.to_euler()
					a.z = math.pi/2
					obj.orientation = a.to_matrix()
				self.verticeFlags.append(obj)

	def hideVerticeLinks(self):
		for flag in self.verticeFlags:
			flag.endObject()
		self.verticeFlags = []

	def countFieldsPoints(self):
		fields = []

		for vertex in self.verticeMap.values():
			pawn = False
			if vertex.pawn:
				pawn = True

			vertexFieldsNb = []
			cities = []
			closed = 0
			for neighbor in vertex.neighbors:
				if neighbor[1] == "open":
					continue
				elif neighbor[1] == "closed":
					closed += 1
					#If a city:
					if neighbor[2]:
						#pdb.set_trace()
						ridePathResult = self.ridePath(vertex.tile, neighbor[2])
						if not ridePathResult[1] and not ridePathResult[0] in cities: #If the city is not open
							cities.append(ridePathResult[0])
				elif neighbor[1] == "linked":
					for cptr,field in enumerate(fields):
						if neighbor[0] in field[0] and cptr not in vertexFieldsNb:
							vertexFieldsNb.append(cptr)
				else:
					print("countFieldPoints: WTF?!")
			if closed == 4:
				continue


			#print(vertex.tile.position.vect(), vertex.internVect)
			if not vertexFieldsNb:
				if pawn:
					fields.append([[vertex], [vertex], cities])
				else:
					fields.append([[vertex], [], cities])
			else:
				vertexFieldsNb = sorted(vertexFieldsNb)
				fields[vertexFieldsNb[0]][0].append(vertex)
				if pawn:
					fields[vertexFieldsNb[0]][1].append(vertex)

				for nb in range(1,len(vertexFieldsNb)):
					for i in range(0,3):
						fields[vertexFieldsNb[0]][i] += fields[vertexFieldsNb[nb]][i]

				for nb in range(0,len(vertexFieldsNb)-1):
					del fields[vertexFieldsNb[len(vertexFieldsNb)-1-nb]]

		for field in fields:
			print(field[2])
			playersPoints = [0,0,0,0,0,0]
			for vertex in field[1]:
				playersPoints[vertex.pawn.player] += vertex.pawn.value
				if vertex.pawn.value == 2:
					self.game.players[vertex.pawn.player].nbBigPawns += 1
				else:
					self.game.players[vertex.pawn.player].nbPawns += 1
				if vertex.pawn.obj:
					vertex.pawn.obj.endObject()
					vertex.pawn.obj = None

				del vertex.pawn
				vertex.pawn = None

			if playersPoints == [0,0,0,0,0,0]:
				continue

			playerWinner = []
			oldPlayerPoints = 0
			for cptr,i in enumerate(playersPoints):
				if i > oldPlayerPoints:
					playerWinner = [cptr]
					oldPlayerPoints = i
				elif i == oldPlayerPoints:
					playerWinner.append(cptr)
			nbPoints = 0
			for i in field[2]:
				nbPoints += 3

			for player in playerWinner:
				self.game.players[player].score += nbPoints
		for player in self.game.players:
			print(player.name, ":", player.score)
		print(len(fields))

	def pawnInField(self, vertex):
		# This is the stack of the tiles that have to be dealed with
		currentVerticeStack = [vertex]
		#This is the old tiles already done:
		verticeArchiveStack = []

		while currentVerticeStack:
			futureVerticeStack = []
			removeStack = []
			for cpt,vertex in enumerate(currentVerticeStack):
				for neighbor in vertex.neighbors:
					if neighbor[0].pawn:
						return True
					if neighbor[1] == "open" or neighbor[1] == "close" or neighbor[0] in verticeArchiveStack:
						continue

					futureVerticeStack.append(neighbor[0])

				verticeArchiveStack.append(vertex)
				removeStack.append(cpt)

			removeStack = sorted(removeStack)
			for i in range(0, len(removeStack)):
				del currentVerticeStack[len(removeStack)-1-i]

			for i in futureVerticeStack:
				existAlready = False
				for k in currentVerticeStack:
					if k == i:
						existAlready = True
						break
				if not existAlready:
					currentVerticeStack.append(i)

		return False

	def ridePath(self, tile, element):
		isOpen = False

		# This is the stack of the tiles that have to be dealed with
		currentTileStack = [ [tile, copy.deepcopy(element.sides)] ]
		#This is the old tiles already done:
		tileArchiveStack = []
		elementsArchive = [element]

		while currentTileStack:
			futureTileStack = []
			removeStack = []
			for cpt,tile in enumerate(currentTileStack):
				for side in tile[1]:
					vect = convertSideToVector(side)

					pos = Position([tile[0].position.x+vect[0], tile[0].position.y+vect[1]])
					if not pos in self.map:
						isOpen = True
						continue
					if pos in tileArchiveStack:
						continue
					newTile = self.map[pos][0]
					opposedSide = loopInt(side+2, 3)
					possibleSides = []

					for e in newTile.elements:
						boule = False
						if e.name == element.name:
							for eSide in e.sides:
								if eSide == opposedSide:
									possibleSides = copy.deepcopy(e.sides)
									elementsArchive.append(e)
									boule = True
									break
							if boule:
								break

					for cptr,i in enumerate(possibleSides):
						if i == opposedSide:
							del possibleSides[cptr]
							break
					futureTileStack.append([newTile, possibleSides])

				tileArchiveStack.append(tile[0].position)
				removeStack.append(cpt)

			removeStack = sorted(removeStack)
			for i in range(0, len(removeStack)):
				del currentTileStack[len(removeStack)-1-i]

			for i in futureTileStack:
				existAlready = False
				for k in currentTileStack:
					if k[0] == i[0]:
						existAlready = True
						break
				if not existAlready:
					currentTileStack.append(i)

		return [tileArchiveStack, isOpen, elementsArchive]
