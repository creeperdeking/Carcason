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

		self.currentTile = Tile("") # The name of the upper tile in the stack
		self.currentTileObj = logic.getCurrentScene().objects["tile"]

		self.players = [] # Store the players, filled by loadMapFromFile
		self.tileStack = [] # Store the tile Stack
		self.abbeyList = [] # The list of abbey positions
		self.possiblePos = [] # Store the possible position that the currentTile can take
		self.possiblePosFlags = [] # Store the objects added to show possiblePos
		self.pawnObj = dict() # The list of pawns

		self.tiles = dict() # Store the different possible tiles
		self.map = dict() #Contain the whole map, a this: self.map[Position([0,1])] = []

		self.pawnPut = False # If the pawn is already put in this turn
		self.tilePut = True # If the tile is already put this turn

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
		elements = dict()
		for line in fileTable:
			if line == ';':
				self.tiles[tileID] = Tile(tileID, elements)
				first = True
				elements = dict()
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
				if len(words) == 0:
					elements[name] = []
				else:
					elements[name] = list(map(int, words[0].split(',')))
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
					self.addPawn(position, pawnCarac[1], int(pawnCarac[0]))
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
				pawnsString += str(pawn.player)+":"+pawn.element+" "
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

	def convertSideToVector(self, side):
		sideVect = []
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
		return sideVect

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
		self.showPossiblePos()
		self.updateTiles()
		return True

	def addTile(self, tileID, position, rotation):
		if tileID == "tile.019" or tileID == "tile.020":
			self.abbeyList.append(position)

		newTile = copy.deepcopy(self.tiles[tileID])
		newTile.rotation = rotation
		newTile.position = position

		tileObj = self.scene.addObject(tileID)
		tileObj.position[0] = position.x
		tileObj.position[1] = position.y
		a = tileObj.orientation.to_euler()
		a.z = self.currentTile.rotation * math.pi/2
		tileObj.orientation = a.to_matrix()

		self.map[position] = [newTile, tileObj]

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

		return True

	def addPawn(self, position, elementID, player):
		tile = self.map[position][0]
		tile.addPawn(player, elementID)
		#import pdb; pdb.set_trace()
		pawnObj = self.scene.addObject("pawn.00"+str(player+1))
		self.pawnObj[position] = [pawnObj, elementID]

		side = 4
		if tile.elements[elementID]:
			side = loopInt(tile.elements[elementID][0]+tile.rotation, 3)

		#converting side:
		sideVect = self.convertSideToVector(side)

		pawnObj.position[0] = position.x + sideVect[0]*.30
		pawnObj.position[1] = position.y + sideVect[1]*.30

		self.pawnPut = True
		return True

	def ridePath(self, element):
		isOpen = False
		genericElement = element.split('_')[0]

		# This is the stack of the tiles that have to be dealed with
		currentTileStack = [ [self.currentTile, self.currentTile.elements[element]] ]
		#This is the old tiles already done:
		tileArchiveStack = []

		while currentTileStack:
			futureTileStack = []
			removeStack = []
			for cpt,tile in enumerate(currentTileStack):
				for side in tile[1]:
					side = loopInt(side+tile[0].rotation, 3)
					vect = self.convertSideToVector(side)

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
						if e.split('_')[0] == genericElement:
							for a in newTile.elements[e]:
								if loopInt(a+newTile.rotation, 3) == opposedSide:
									possibleSides = copy.copy(newTile.elements[e])
									boule = True
									break
							if boule:
								break

					for cptr,i in enumerate(possibleSides):
						if loopInt(i+newTile.rotation, 3) == opposedSide:
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

		return [tileArchiveStack, isOpen]

	def putPawn(self, elementID):
		if self.pawnPut or self.player.nbPawns == 0:
			return False

		tileArchiveStack = self.ridePath(elementID)[0]

		genericElement = elementID.split('_')[0]
		if elementID != "field":
			for tilePos in tileArchiveStack:
				for pawn in self.map[tilePos][0].pawns:
					if pawn.element.split('_')[0] == genericElement:
						return False

		self.addPawn(self.currentTile.position, elementID, self.currentPlayer)
		self.player.nbPawns -= 1

		self.pawnPut = True
		return True

	def countPoints(self):
		for element in self.currentTile.elements:
			genericElement = element.split('_')[0]
			if genericElement == "field" or genericElement == "abbey":
				continue

			ridePathResult = self.ridePath(element)
			tileArchiveStack = ridePathResult[0]
			isOpen = ridePathResult[1]
			if isOpen:
				continue

			playersPoints = [0,0,0,0,0,0]
			for tilePos in tileArchiveStack:
				for cp,pawn in enumerate(self.map[tilePos][0].pawns):
					if pawn.element.split('_')[0] == genericElement:
						print("Rendre pion "+self.players[pawn.player].name)
						playersPoints[int(pawn.player)] += 1
						self.players[pawn.player].nbPawns += 1
						if tilePos in self.pawnObj:
							pawnObj = self.pawnObj[tilePos]
							if pawnObj[1] == genericElement:
								pawnObj[0].endObject()
								del self.pawnObj[tilePos]
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

			for player in playerWinner:
				self.players[player].score += len(tileArchiveStack)*2

		for ptrcp,abbeyPos in enumerate(self.abbeyList):
			if Position([abbeyPos.x, abbeyPos.y+1]) in self.map and Position([abbeyPos.x+1, abbeyPos.y+1]) in self.map and Position([abbeyPos.x+1, abbeyPos.y]) in self.map and Position([abbeyPos.x+1, abbeyPos.y-1]) in self.map and Position([abbeyPos.x, abbeyPos.y-1]) in self.map and Position([abbeyPos.x-1, abbeyPos.y-1]) in self.map and Position([abbeyPos.x-1, abbeyPos.y]) in self.map and Position([abbeyPos.x-1, abbeyPos.y-1]) in self.map:
				for cp,pawn in enumerate(self.map[abbeyPos][0].pawns):
					if pawn.element == "abbey":
						for cptr in range(0, len(self.players)):
							if pawn.player == cptr:
								pObj = self.pawnObj[abbeyPos]
								if pObj[1] == "abbey":
									pObj[0].endObject()
									del self.map[abbeyPos][0].pawns[cp]
								self.players[cptr].score += 9

	def rotateTile(self):
		self.currentTile.rotate()

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
