import bge
import bge.logic as logic
import bge.events as events
from scripts.utils import *
from scripts.tile import *
import math
import copy
from mathutils import Matrix
import random
import pdb

#The class holding the whole game
class Game:
	def __init__(self, tileFilePath, mapFilePath, defaultStackPath):
		self.scene = logic.getCurrentScene()

		self.tiles = dict() # Store the different possible tiles
		self.map = dict() #Contain the whole map, a this: self.map[Position([0,1])] = []
		self.verticeMap = dict() #Store the vertices by position, like self.map

		self.currentTile = Tile("") # The name of the upper tile in the stack
		self.currentTileObj = logic.getCurrentScene().objects["tile"]

		self.players = [] # Store the players, filled by loadMapFromFile
		self.tileStack = [] # Store the tile Stack
		self.abbeyList = [] # The list of abbey positions
		self.possiblePos = [] # Store the possible position that the currentTile can take
		self.possiblePosFlags = [] # Store the objects added to show possiblePos
		self.verticeFlags = []
		self.pawnsObj = dict() # The list of pawns

		self.pawnPut = False # If the pawn is already put in this turn
		self.tilePut = True # If the tile is already put this turn
		self.showLinks = 0

		self.camTracer = self.scene.objects["camera"]

		self.loadTilesFromFile(tileFilePath) # Load the tiles caracteristics
		self.loadMapFromFile(mapFilePath, defaultStackPath) # Load a save
		self.updateTiles()

		self.nextTurn() # Let the show begin

	def loadTilesFromFile(self, filePath):
		self.tiles = dict()

		configFile = open(filePath, "r")
		fileContent = configFile.read()
		fileTable = fileContent.split("\n")

		first = True
		tileID = ""
		elements = []
		for line in fileTable:
			if line == ';':

				self.tiles[tileID] = Tile(tileID, elements)
				first = True
				elements = []
				continue

			if first == True:
				tileID = line
				first = False
			else:
				words = line.split(' ')
				name = words[0]
				del words[0]
				#A tile element is defined as this:
				#example: elements["tile.001"] = [[0,1]]
				elements.append(Element(name,list(map(int, words[1].split(','))), int(words[0])))
		configFile.close()

	def loadMapFromFile(self, filePath, defaultStackPath):
		self.map = dict()

		configFile = open(filePath, "r")
		fileContent = configFile.read()
		fileTable = fileContent.split("\n")

		self.currentPlayer = int(fileTable[0])
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
				self.players.append(player)
			#Second step, setup the map
			elif step == 1:
				position = Position(words[0].split(','))
				tile = self.addTile(words[1], position, int(words[2]))

				for v in range(0,3):
					del words[0]

				for j in words:
					pawnCarac = j.split(':')
					element = tile.getElement(pawnCarac[1], int(pawnCarac[2]))

					self.addPawn(position, element, int(pawnCarac[3]), int(pawnCarac[0]))
			#Third step, setup the tile stack:
			else:
				self.tileStack = list(words)
				break

		if self.tileStack[0] == "none":
			defaultStackFile = open(defaultStackPath, "r")
			fileContent = defaultStackFile.read()
			fileTab = fileContent.split('\n')[0].split(' ')
			random.shuffle(fileTab)
			self.tileStack = fileTab
		self.updateVerticeLinks()
		configFile.close()

	def saveMap(self, filePath):
		configFile = open(filePath, "w")
		configFile.write(str(self.currentPlayer)+"\n")
		for player in self.players:
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

		for cptr,tileID in enumerate(self.tileStack):
			configFile.write(tileID)
			if cptr != len(self.tileStack)-1:
				configFile.write(" ")
		configFile.close()

	def updateCurrentTileView(self, tilePos):
		if self.tilePut == False:
			self.currentTileObj.position[0] = tilePos.x
			self.currentTileObj.position[1] = tilePos.y
			a = self.currentTileObj.orientation.to_euler()
			a.z = self.currentTile.rotation * math.pi/2
			self.currentTileObj.orientation = a.to_matrix()
			self.currentTile.position = tilePos

	def updateTiles(self):
		for key in self.map:
			self.map[key][1].position[0] = key.x
			self.map[key][1].position[1] = key.y
			a = self.map[key][1].orientation.to_euler()
			a.z = self.map[key][0].rotation * math.pi/2
			self.map[key][1].orientation = a.to_matrix()

	def nextTurn(self):
		if len(self.tileStack) == 0:
			return False
		if self.tilePut == False:
			return True
		self.pawnPut = False
		self.tilePut = False

		self.currentPlayer = int(loopInt(self.currentPlayer+1, len(self.players)-1))
		self.player = self.players[self.currentPlayer]
		print("\n New Turn: player="+self.player.name)

		while 2+2 != 5:
			self.currentTile = copy.deepcopy(self.tiles[self.tileStack[0]])

			if not self.findPossiblePos(): #Refresh possibles tiles positions
				self.tileStack.append(self.tileStack[0])
				del self.tileStack[0]
			else:
				break
		self.currentTileObj = self.scene.addObject(self.tileStack[0])
		self.currentTileObj.position[2] = -.005
		self.showPossiblePos()
		self.updateTiles()

		return True

	def addTile(self, tileID, position, rotation):
		if tileID == "tile.019" or tileID == "tile.020":
			self.abbeyList.append(position)

		newTile = copy.deepcopy(self.tiles[tileID])
		newTile.rotate(rotation, True)
		newTile.position = position
		newTile.createVertice(self.verticeMap)

		tileObj = self.scene.addObject(tileID)
		tileObj.position[0] = position.x
		tileObj.position[1] = position.y
		tileObj.position[2] = 0
		a = tileObj.orientation.to_euler()
		a.z = self.currentTile.rotation * math.pi/2
		tileObj.orientation = a.to_matrix()


		self.map[position] = [newTile, tileObj]
		return newTile

	def putTile(self, position):
		if self.tilePut:
			return False
		# Testing if the rotation and the position of the tile is correct
		possiblePos = False
		for pos in self.possiblePos:
			if position == pos[0]:
				possiblePos = True
				if not self.currentTile.rotation in pos[1]:
					return False
		if not possiblePos:
			return False

		self.hidePossiblePos()

		print("Putting tile")
		self.addTile(self.currentTile.ID, position, self.currentTile.rotation)
		del self.tileStack[0]
		self.tilePut = True

		self.updateVerticeLinks()
		return True

	def addPawn(self, position, element, value, player):
		tile = self.map[position][0]

		pawnObj = None
		if value == 2:
			pawnObj = self.scene.addObject("bigPawn.00"+str(player+1))
		else:
			pawnObj = self.scene.addObject("pawn.00"+str(player+1))
		self.pawnsObj[position] = [pawnObj, element]
		tile.addPawn(player, element, value, pawnObj)
		side = element.sides[0]

		#converting side:
		sideVect = convertSideToVector(side)
		modif = .3
		if side > 4:
			modif = .2
		pawnObj.position[0] = position.x + sideVect[0]*modif
		pawnObj.position[1] = position.y + sideVect[1]*modif

		self.pawnPut = True
		return True

	def ridePath(self, element):
		isOpen = False

		# This is the stack of the tiles that have to be dealed with
		currentTileStack = [ [self.currentTile, copy.deepcopy(element.sides)] ]
		#This is the old tiles already done:
		tileArchiveStack = []
		elementsArchive = [element]

		while currentTileStack:
			#pdb.set_trace()
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

	def putPawn(self, element, value):
		if self.pawnPut or value == 1 and self.player.nbPawns == 0 or value == 2 and self.player.nbBigPawns == 0:
			return False

		if element.name == "empty":
			return False

		if element.sides[0] < 4:
			tileArchiveStack = self.ridePath(element)[0]

			for tilePos in tileArchiveStack:
				for pawn in self.map[tilePos][0].pawns:
					if pawn.element.name == element.name:
						return False

		self.addPawn(self.currentTile.position, element, value, self.currentPlayer)
		if value == 2:
			self.player.nbBigPawns -= 1
		else:
			self.player.nbPawns -= 1

		self.pawnPut = True
		return True

	def countPoints(self):
		print("DEBUG: counting points")
		for element in self.currentTile.elements:
			if element.name == "empty" or element.name == "abbey" or element.name == "field":
				continue

			ridePathResult = self.ridePath(element)
			tileArchiveStack = ridePathResult[0]
			isOpen = ridePathResult[1]

			if isOpen:
				continue

			playersPoints = [0,0,0,0,0,0]
			for tilePos in tileArchiveStack:
				for cp,pawn in enumerate(self.map[tilePos][0].pawns):
					if pawn.element.name == element.name:
						playersPoints[int(pawn.player)] += pawn.value
						if pawn.value == 2:
							self.players[pawn.player].nbBigPawns += 1
						else:
							self.players[pawn.player].nbPawns += 1
						if tilePos in self.pawnsObj:
							pawnObj = self.pawnsObj[tilePos]
							if pawnObj[1].name == element.name:
								pawnObj[0].endObject()
								del self.pawnsObj[tilePos]
						del self.map[tilePos][0].pawns[cp]
						break

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
			for result in ridePathResult[2]:
				nbPoints += result.value

			for player in playerWinner:
				self.players[player].score += nbPoints

		for ptrcp,abbeyPos in enumerate(self.abbeyList):
			if Position([abbeyPos.x, abbeyPos.y+1]) in self.map and Position([abbeyPos.x+1, abbeyPos.y+1]) in self.map and Position([abbeyPos.x+1, abbeyPos.y]) in self.map and Position([abbeyPos.x+1, abbeyPos.y-1]) in self.map and Position([abbeyPos.x, abbeyPos.y-1]) in self.map and Position([abbeyPos.x-1, abbeyPos.y-1]) in self.map and Position([abbeyPos.x-1, abbeyPos.y]) in self.map and Position([abbeyPos.x-1, abbeyPos.y-1]) in self.map:
				for cp,pawn in enumerate(self.map[abbeyPos][0].pawns):
					if pawn.element.name == "abbey":
						for cptr in range(0, len(self.players)):
							if pawn.player == cptr:
								pObj = self.pawnsObj[abbeyPos]
								if pObj[1].name == "abbey":
									pObj[0].endObject()
									del self.map[abbeyPos][0].pawns[cp]
								self.players[cptr].score += 9
								self.players[cptr].nbPawns += 1

	def countFieldsPoints(self):
		fields = []

		for vertex in self.verticeMap.values():
			pawn = False
			if vertex.pawn:
				pawn = True

			vertexFieldsNb = []
			isOpen = False
			closed = 0
			for neighbor in vertex.neighbors:
				if neighbor[1] == "open":
					isOpen = True
				elif neighbor[1] == "closed":
					closed += 1
					continue
				elif neighbor[1] == "linked":
					for cptr,field in enumerate(fields):
						if neighbor[0] in field[0] and cptr not in vertexFieldsNb:
							vertexFieldsNb.append(cptr)
				else:
					print("countFieldPoints: WTF?!")
			if closed == 4:
				continue

			if not vertexFieldsNb:
				if pawn:
					fields.append([[vertex], isOpen, [vertex.pawn]])
				else:
					fields.append([[vertex], isOpen, []])
			else:
				vertexFieldsNb = sorted(vertexFieldsNb)
				fields[vertexFieldsNb[0]][0].append(vertex)
				if isOpen:
					fields[vertexFieldsNb[0]][1] = True
				if pawn:
					fields[vertexFieldsNb[0]][2].append(vertex.pawn)
				#pdb.set_trace()
				for nb in range(1,len(vertexFieldsNb)):
					fields[vertexFieldsNb[0]][0] += fields[vertexFieldsNb[nb]][0]

				for nb in range(0,len(vertexFieldsNb)-1):
					del fields[vertexFieldsNb[len(vertexFieldsNb)-1-nb]]

		playersPoints = [0,0,0,0,0,0]
		for field in fields:
			for pawn in field[2]:
				playersPoints[pawn.player] += pawn.value
				if pawn.value == 2:
					self.players[pawn.player].nbBigPawns += 1
				else:
					self.players[pawn.player].nbPawns += 1
				pawn.obj.endObject()
				del pawn

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
			nbPoints = 6

			for player in playerWinner:
				self.players[player].score += nbPoints

		print(len(fields))

	def rotateTile(self, plus=1):
		self.currentTile.rotate(plus)

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
					possibilities.append(self.currentTile.isCompatibleWith(0, self.map[Position([posPos[0].x, posPos[0].y+1])][0]))
				if Position([posPos[0].x+1, posPos[0].y]) in self.map:
					possibilities.append(self.currentTile.isCompatibleWith(3, self.map[Position([posPos[0].x+1, posPos[0].y])][0]))
				if Position([posPos[0].x, posPos[0].y-1]) in self.map:
					possibilities.append(self.currentTile.isCompatibleWith(2, self.map[Position([posPos[0].x, posPos[0].y-1])][0]))
				if Position([posPos[0].x-1, posPos[0].y]) in self.map:
					possibilities.append(self.currentTile.isCompatibleWith(1, self.map[Position([posPos[0].x-1, posPos[0].y])][0]))
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
				pos = [tile.position.x - 0.5 + vertex.internVect[0]/2 +.25 + neighbor[2][0]/8,
						tile.position.y - 0.5 + vertex.internVect[1]/2 +.25 + neighbor[2][1]/8,
						1]
				obj = self.scene.addObject("line.black")
				if neighbor[1] == "closed":
					obj = self.scene.addObject("line.red")
				elif neighbor[1] == "linked":
					obj = self.scene.addObject("line.green")
				elif neighbor[1] == "open":
						obj = self.scene.addObject("line.white")
				obj.position = pos
				if abs(neighbor[2][1]) == 1:
					a = obj.orientation.to_euler()
					a.z = math.pi/2
					obj.orientation = a.to_matrix()
				self.verticeFlags.append(obj)

	def hideVerticeLinks(self):
		for flag in self.verticeFlags:
			flag.endObject()
		self.verticeFlags = []

	def endGame(self):
		winner = 0
		self.countFieldsPoints()
		for cptr,player in enumerate(self.players):
			if player.score > self.players[winner].score:
				winner = cptr
		obj = self.scene.addObject("pawn.00"+str(winner+1))
		obj.scaling *= 9
		obj.position = self.camTracer.position
		obj.position.z = 0
