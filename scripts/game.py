# Fait par Antoine Gros, c'est le meilleur et c'est celui qui l'a fait vraiment!
import bge
import bge.logic as logic
import bge.events as events
from scripts.utils import *
from scripts.tile import *
import math
import copy
from mathutils import Matrix
import random

class Player:
	def __init__(self, name):
		self.name = name
		self.nbPawns = int(7)
		self.nbBigPawns = 1

		self.score = 0

#The class holding the whole game
class Game:
	def __init__(self, tileFilePath, mapFilePath, defaultStackPath):
		self.scene = logic.getCurrentScene()

		self.currentTile = Tile("") # The name of the upper tile in the stack
		self.tileObj = logic.getCurrentScene().objects["tile"]
		self.possiblePos = [] # Store the possible position that the currentTile can take
		self.possiblePosFlags = []

		self.abbeyList = []

		self.pawnPut = False # If the pawn is already put in this turn
		self.tilePut = True # If the tile is already put this turn

		self.pawnObj = dict()
		self.players = [] # Store the players, filled by loadMapFromFile
		self.loadTilesFromFile(tileFilePath) # Load the tiles caracteristics
		self.tileStack = [] # Store the tile Stack
		self.loadMapFromFile(mapFilePath, defaultStackPath) # Load a save

		self.nextTurn()

	def loadTilesFromFile(self, filePath):
		self.tiles = dict()

		configFile = open(filePath, "r")
		fileContent = configFile.read()
		fileTable = fileContent.split("\n")

		first = True
		tileID = str()
		elements = dict()
		for element in fileTable:
			if element == ';':
				self.tiles[tileID] = Tile(tileID, elements)
				first = True
				elements = {}
				continue

			if first == True:
				tileID = element
				first = False
			else:
				words = element.split(' ')
				name = words[0]
				del words[0]
				#A tile element is defined as this:
				#example: self.elements = ['',[0,1]]
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

		step = 0
		self.currentPlayer = int(fileTable[0])
		del fileTable[0]
		for cptr,i in enumerate(fileTable):
			if i == '':
				continue
			if i == ';':
				step+=1
				continue

			elements = i.split(' ')
			if step == 0:
				player = Player(elements[0])
				player.nbPawns = int(elements[1])
				player.nbGreatPawn = int(elements[2])
				player.score = int(elements[3])
				self.players.append(player)
			elif step == 1:
				position = elements[0].split(',')
				tileID = elements[1]
				tile = copy.deepcopy(self.tiles[tileID])
				tile.rotation = int(elements[2])
				tile.position = Position(position)
				if tile.ID == "tile.019" or tile.ID == "tile.020":
					self.abbeyList.append(tile.position)
				for v in range(0,3):
					del elements[0]

				pawnTab = []
				for j in elements:
					pawnCarac = j.split(':')
					tile.addPawn(pawnCarac[0], pawnCarac[1])

				#import pdb; pdb.set_trace()
				for pawn in tile.pawns:
					pawnObj = self.scene.addObject("pawn.00"+str(int(pawn.player)+1))
					if tile.elements[pawn.element] == []:
						sideVect = [0,0]
					else:
						sideVect = self.convertSideToVector(loopInt(tile.elements[pawn.element][0]+tile.rotation, 3))

					pawnObj.position[0] = int(position[0]) + sideVect[0]*.30
					pawnObj.position[1] = int(position[1]) + sideVect[1]*.30
					self.pawnObj[tile.position] = [pawnObj, pawn.element]


				scene = logic.getCurrentScene()
				newTileObj = scene.addObject(tileID)

				newTile = [tileID,tile,newTileObj]

				self.map[Position(position)] = newTile
			else:
				self.tileStack = list(elements)
				break
		if self.tileStack[0] == "none":
			defaultStackFile = open(defaultStackPath, "r")
			fileContent = defaultStackFile.read()
			fileTab = fileContent.split(' ')
			random.shuffle(fileTab)
			self.tileStack = fileTab

		configFile.close()

	def saveMap(self, filePath):
		configFile = open(filePath, "w")
		configFile.write(str(self.currentPlayer)+"\n")
		for player in self.players:
			configFile.write(" ".join([player.name,str(player.nbPawns),str(player.nbBigPawns), str(player.score)])+"\n")
		configFile.write(";\n")

		for cle in self.map:
			tile = self.map[cle]
			pawnsString = " "

			for pawn in tile[1].pawns:
				pawnsString += str(pawn.player)+":"+pawn.element+" "
			pawnsString = pawnsString[:-1]
			configFile.write(str(cle.x)+","+str(cle.y)+" "+tile[0]+" "+str(tile[1].rotation)+pawnsString+"\n")
		configFile.write(";\n")

		for cptr,tileID in enumerate(self.tileStack):
			configFile.write(tileID)
			if cptr != len(self.tileStack)-1:
				configFile.write(" ")
		configFile.close()

	def updateTiles(self, tilePos):
		if self.tilePut == False:
			self.tileObj.position[0] = tilePos.x
			self.tileObj.position[1] = tilePos.y
			a = self.tileObj.orientation.to_euler()
			a.z = self.currentTile.rotation * math.pi/2
			self.tileObj.orientation = a.to_matrix()
			self.currentTile.position = tilePos

		for key in self.map:
			self.map[key][2].position[0] = key.x
			self.map[key][2].position[1] = key.y
			a = self.map[key][2].orientation.to_euler()
			a.z = self.map[key][1].rotation * math.pi/2
			self.map[key][2].orientation = a.to_matrix()

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

		self.currentPlayer = loopInt(self.currentPlayer+1, len(self.players)-1)

		self.player = self.players[self.currentPlayer]
		print("New Turn: player="+self.player.name)
		self.currentTile = copy.deepcopy(self.tiles[self.tileStack[0]])
		self.tileObj = self.scene.addObject(self.tileStack[0])
		self.findPossiblePos() #Refresh possibles tiles positions
		self.showPossiblePos()
		return True

	def addTile(self, tileID, position, rotation):
		scene = logic.getCurrentScene()
		if self.currentTile.ID == "tile.019" or self.currentTile.ID == "tile.020":
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
		self.map[position] = [tileID, newTile, tileObj]

	def putTile(self, position):
		if self.tilePut: #or (position in self.possiblePos) == False:
			return False
		possiblePos = False

		for i in self.possiblePos:
			if position == i[0]:
				possiblePos = True
				if not (self.currentTile.rotation in i[1]):
					return False
		if not possiblePos:
			return False
		self.hidePossiblePos()
		print("Putting tile")
		self.addTile(self.currentTile.ID, position, self.currentTile.rotation)
		del self.tileStack[0]
		self.tilePut = True

		return True


	def putPawn(self, elementID, realPawnSide):
		if self.pawnPut or self.player.nbPawns == 0:
			return False
		#import pdb; pdb.set_trace()
		genericElement = elementID.split('_')[0]
		if elementID != "field":
			# This is the stack of the tiles that have to be dealed with
			currentTileStack = [ [self.currentTile, self.currentTile.elements[elementID]] ]
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
							continue
						if pos in tileArchiveStack:
							continue
						newTile = self.map[pos][1]
						opposedSide = loopInt(side+2, 3)
						possibleSides = []
						#import pdb; pdb.set_trace()
						for e in newTile.elements:
							boule = False
							if e.split('_')[0] == genericElement:
								for a in newTile.elements[e]:
									if loopInt(a+newTile.rotation, 3) == opposedSide:
										possibleSides = newTile.elements[e]
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
			#import pdb; pdb.set_trace()
			for tilePos in tileArchiveStack:
				for pawn in self.map[tilePos][1].pawns:
					if pawn.element == elementID:
						return False


		self.map[self.currentTile.position][1].addPawn(self.currentPlayer, elementID)
		pawnObj = self.scene.addObject("pawn.00"+str(self.currentPlayer+1))
		self.pawnObj[self.currentTile.position] = [pawnObj, elementID]

		#converting side:
		sideVect = self.convertSideToVector(realPawnSide)

		pawnObj.position[0] = self.currentTile.position.x + sideVect[0]*.30
		pawnObj.position[1] = self.currentTile.position.y + sideVect[1]*.30
		self.player.nbPawns -= 1

		self.pawnPut = True
		return True

	def countPoints(self):
		#import pdb; pdb.set_trace()

		for element in self.currentTile.elements:
			genericElement = element.split('_')[0]
			if genericElement == "field" or genericElement == "abbey":
				continue

			currentTileStack = [ [self.currentTile, self.currentTile.elements[element]] ]
			tileArchiveStack = []

			open = False
			while currentTileStack:
				futureTileStack = []
				removeStack = []
				for cpt,tile in enumerate(currentTileStack):
					for side in tile[1]:
						side = loopInt(side+tile[0].rotation, 3)
						vect = self.convertSideToVector(side)

						pos = Position([tile[0].position.x+vect[0], tile[0].position.y+vect[1]])
						if not pos in self.map:
							open = True
							break
						if pos in tileArchiveStack:
							continue
						newTile = self.map[pos][1]
						opposedSide = loopInt(side+2, 3)
						possibleSides = []
						#import pdb; pdb.set_trace()
						for e in newTile.elements:
							boule = False
							if e.split('_')[0] == genericElement:
								for a in newTile.elements[e]:
									if loopInt(a+newTile.rotation, 3) == opposedSide:
										possibleSides = newTile.elements[e]
										boule = True
										break
								if boule:
									break

						for cptr,i in enumerate(possibleSides):
							if loopInt(i+newTile.rotation, 3) == opposedSide:
								del possibleSides[cptr]
								break
						futureTileStack.append([newTile, possibleSides])
					if open:
						break
					tileArchiveStack.append(tile[0].position)
					removeStack.append(cpt)
				if open:
					break
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
			if open:
				continue
			#import pdb; pdb.set_trace()
			playersPoints = [0,0,0,0,0,0]
			for tilePos in tileArchiveStack:
				for cp,pawn in enumerate(self.map[tilePos][1].pawns):
					if pawn.element.split('_')[0] == genericElement:
						playersPoints[int(pawn.player)] += 1
						self.players[pawn.player].nbPawns += 1
						if tilePos in self.pawnObj:
							pawnObj = self.pawnObj[tilePos]
							if pawnObj[1] == element:
								pawnObj[0].endObject()
								del self.pawnObj[tilePos]
						del self.map[tilePos][1].pawns[cp]
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
				for cp,pawn in enumerate(self.map[abbeyPos][1].pawns):
					#import pdb; pdb.set_trace()
					if pawn.element == "abbey":
						for cptr in range(0, len(self.players)):
							if pawn.player == cptr:
								pObj = self.pawnObj[abbeyPos]
								if pObj[1] == "abbey":
									pObj[0].endObject()
									del self.map[abbeyPos][1].pawns[cp]
								self.players[cptr].score += 9

		for player in self.players:
			print(player.name, ":", player.score)

	def rotateTile(self):
		self.currentTile.rotate()

	def findPossiblePos(self):
		self.possiblePos = []

		for cle in self.map:
			pp = []
			for i in self.possiblePos:
				pp.append(i[0])
			if not Position([cle.x, cle.y+1]) in self.map:
				if not Position([cle.x, cle.y+1]) in pp:
					self.possiblePos.append([Position([cle.x, cle.y+1]), []])
			if not Position([cle.x+1, cle.y]) in self.map:
				if not Position([cle.x+1, cle.y]) in pp:
					self.possiblePos.append([Position([cle.x+1, cle.y]), []])
			if not Position([cle.x, cle.y-1]) in self.map:
				if not Position([cle.x, cle.y-1]) in pp:
					self.possiblePos.append([Position([cle.x, cle.y-1]), []])
			if not Position([cle.x-1, cle.y]) in self.map:
				if not Position([cle.x-1, cle.y]) in pp:
					self.possiblePos.append([Position([cle.x-1, cle.y]), []])

			badPos = []
			for cptr,i in enumerate(self.possiblePos):
				goodSides = []
				# Get, for each side of the possible position, the list of compatible rotations
				possibilities = []
				if Position([i[0].x, i[0].y+1]) in self.map:
					possibilities.append(self.currentTile.isCompatibleWith(0, self.map[Position([i[0].x, i[0].y+1])][1]))
				if Position([i[0].x+1, i[0].y]) in self.map:
					possibilities.append(self.currentTile.isCompatibleWith(3, self.map[Position([i[0].x+1, i[0].y])][1]))
				if Position([i[0].x, i[0].y-1]) in self.map:
					possibilities.append(self.currentTile.isCompatibleWith(2, self.map[Position([i[0].x, i[0].y-1])][1]))
				if Position([i[0].x-1, i[0].y]) in self.map:
					possibilities.append(self.currentTile.isCompatibleWith(1, self.map[Position([i[0].x-1, i[0].y])][1]))
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
				i[1] = goodSides
				if nbBadSide == 4:
					badPos.append(cptr)

			badPos = sorted(badPos)
			for i in range(0,len(badPos)):
				del self.possiblePos[badPos[len(badPos)-1-i]]

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
