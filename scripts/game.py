"""
Copyright © <01/08/2017>, <Alexis Gros>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
Except as contained in this notice, the name of the <copyright holders> shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the <copyright holders>.
"""


import math
import copy
from mathutils import Matrix
import random
import pdb

import bge
import bge.logic as logic
import bge.events as events

from scripts.utils import *
from scripts.tile import *
from scripts.map import *
from scripts.UI import *

#The class holding the whole game
class Game:
	def __init__(self, tileFilePath, mapFilePath, defaultStackPath):
		self.scene = logic.getCurrentScene()

		self.interface = UI()

		self.tiles = dict() # Store the different possible tiles
		self.map = CarcaMap(self) #Contain the whole map, a this: self.map.map[Position([0,1])] = []

		self.currentTile = Tile("") # The name of the upper tile in the stack
		self.currentTileObj = logic.getCurrentScene().objects["tile"]

		self.players = [] # Store the players, filled by loadMapFromFile
		self.tileStack = [] # Store the tile Stack
		self.abbeyList = [] # The list of abbey positions

		self.pawnsObj = dict() # The list of pawns

		self.pawnPut = False # If the pawn is already put in this turn
		self.tilePut = True # If the tile is already put this turn

		self.camTracer = self.scene.objects["camera"]

		self.loadTilesFromFile(tileFilePath) # Load the tiles caracteristics
		self.map.loadMapFromFile(mapFilePath, defaultStackPath) # Load a save
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

	def updateCurrentTileView(self, tilePos):
		if self.tilePut == False:
			self.currentTileObj.position[0] = tilePos.x
			self.currentTileObj.position[1] = tilePos.y
			a = self.currentTileObj.orientation.to_euler()
			a.z = self.currentTile.rotation * math.pi/2
			self.currentTileObj.orientation = a.to_matrix()
			self.currentTile.position = tilePos

	def updateTiles(self):
		for key in self.map.map:
			self.map.map[key][1].position[0] = key.x
			self.map.map[key][1].position[1] = key.y
			a = self.map.map[key][1].orientation.to_euler()
			a.z = self.map.map[key][0].rotation * math.pi/2
			self.map.map[key][1].orientation = a.to_matrix()

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
		print("Remaining tiles:", len(self.tileStack))
		self.interface.setPlayer(self.currentPlayer)

		while 2+2 != 5:
			self.currentTile = copy.deepcopy(self.tiles[self.tileStack[0]])

			if not self.map.findPossiblePos(): #Refresh possibles tiles positions
				self.tileStack.append(self.tileStack[0])
				del self.tileStack[0]
			else:
				break
		self.currentTileObj = self.scene.addObject(self.tileStack[0])
		self.currentTileObj.position[2] = -.05
		self.map.showPossiblePos()
		self.updateTiles()

		self.interface.update(len(self.tileStack), self.players)

		return True

	def addTile(self, tileID, position, rotation):
		if tileID == "tile.019" or tileID == "tile.020":
			self.abbeyList.append(position)

		newTile = copy.deepcopy(self.tiles[tileID])
		newTile.rotate(rotation, True)
		newTile.position = position
		newTile.createVertice(self.map.verticeMap)

		tileObj = self.scene.addObject(tileID)
		tileObj.position[0] = position.x
		tileObj.position[1] = position.y
		tileObj.position[2] = 0
		a = tileObj.orientation.to_euler()
		a.z = self.currentTile.rotation * math.pi/2
		tileObj.orientation = a.to_matrix()


		self.map.map[position] = [newTile, tileObj]
		return newTile

	def putTile(self, position):
		if self.tilePut:
			return False
		# Testing if the rotation and the position of the tile is correct
		possiblePos = False
		for pos in self.map.possiblePos:
			if position == pos[0]:
				possiblePos = True
				if not self.currentTile.rotation in pos[1]:
					return False
		if not possiblePos:
			return False

		self.map.hidePossiblePos()

		print("Putting tile")
		self.addTile(self.currentTile.ID, position, self.currentTile.rotation)
		del self.tileStack[0]
		self.tilePut = True

		self.map.updateVerticeLinks()
		return True

	def addPawn(self, position, element, value, player):
		tile = self.map.map[position][0]

		pawnObj = None
		if value == 2:
			pawnObj = self.scene.addObject("bigPawn.00"+str(player+1))
		else:
			pawnObj = self.scene.addObject("pawn.00"+str(player+1))
		if not tile.addPawn(player, element, value, pawnObj):
			pawnObj.endObject()
			return False
		self.pawnsObj[position] = [pawnObj, element]

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

	def putPawn(self, element, value):
		if self.pawnPut or value == 1 and self.player.nbPawns == 0 or value == 2 and self.player.nbBigPawns == 0 or element.name == "empty":
			return False

		if element.sides[0] < 4:
			tileArchiveStack = self.map.ridePath(self.currentTile, element)[0]

			for tilePos in tileArchiveStack:
				for pawn in self.map.map[tilePos][0].pawns:
					if pawn.element.name == element.name:
						return False
		else:
			vertex = self.map.map[self.currentTile.position][0].vertices[element.sides[0]-5]
			if self.map.pawnInField(vertex):
				return False

		if not self.addPawn(self.currentTile.position, element, value, self.currentPlayer):
			print("dfdfdf")
			return False
		if value == 2:
			self.player.nbBigPawns -= 1
		else:
			self.player.nbPawns -= 1

		self.pawnPut = True
		return True

	def countPoints(self):
		for element in self.currentTile.elements:
			if element.name == "empty" or element.name == "abbey" or element.name == "field":
				continue

			ridePathResult = self.map.ridePath(self.currentTile, element)
			tileArchiveStack = ridePathResult[0]
			isOpen = ridePathResult[1]

			if isOpen:
				continue

			playersPoints = [0,0,0,0,0,0]
			for tilePos in tileArchiveStack:
				for cp,pawn in enumerate(self.map.map[tilePos][0].pawns):
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
						del self.map.map[tilePos][0].pawns[cp]
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
			if Position([abbeyPos.x, abbeyPos.y+1]) in self.map.map and Position([abbeyPos.x+1, abbeyPos.y+1]) in self.map.map and Position([abbeyPos.x+1, abbeyPos.y]) in self.map.map and Position([abbeyPos.x+1, abbeyPos.y-1]) in self.map.map and Position([abbeyPos.x, abbeyPos.y-1]) in self.map.map and Position([abbeyPos.x-1, abbeyPos.y-1]) in self.map.map and Position([abbeyPos.x-1, abbeyPos.y]) in self.map.map and Position([abbeyPos.x-1, abbeyPos.y-1]) in self.map.map:
				for cp,pawn in enumerate(self.map.map[abbeyPos][0].pawns):
					if pawn.element.name == "abbey":
						for cptr in range(0, len(self.players)):
							if pawn.player == cptr:
								pObj = self.pawnsObj[abbeyPos]
								if pObj[1].name == "abbey":
									pObj[0].endObject()
									del self.map.map[abbeyPos][0].pawns[cp]
								self.players[cptr].score += 9
								self.players[cptr].nbPawns += 1

	def rotateTile(self, plus=1):
		self.currentTile.rotate(plus)

	def endGame(self):
		winner = 0
		self.map.countFieldsPoints()
		for cptr,player in enumerate(self.players):
			if player.score > self.players[winner].score:
				winner = cptr
		obj = self.scene.addObject("pawn.00"+str(winner+1))
		obj.scaling *= 9
		obj.position = self.camTracer.position
		obj.position.z = 5
