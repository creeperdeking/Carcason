"""
Copyright © <01/08/2017>, <Alexis Gros>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
Except as contained in this notice, the name of the <copyright holders> shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the <copyright holders>.
"""

import bge.logic as logic

class UI:
	def __init__(self):
		self.scene = logic.getSceneList()[1]

		self.playerFlag = self.scene.objects["playerflagflag"]
		self.playerFlagObject = None
		self.currentPlayer = 0

		self.affPlayers = False

		self.affObjList = []

	def showNbr(self, number, parentObjectName):
		number = str(number)
		for cptr,i in enumerate(number):
			obj = self.scene.addObject(i)
			parent = self.scene.objects[parentObjectName]
			obj.position = parent.position

			obj.position[0] += cptr*.60*parent.scaling[0]
			obj.scaling = [parent.scaling[0],parent.scaling[0],parent.scaling[0]]
			self.affObjList.append(obj)

	def clearObjList(self):
		for obj in self.affObjList:
			obj.endObject()
		self.affObjList = []

	def update(self, nbTiles, playersRef):
		if not self.affPlayers:
			for cptr,player in enumerate(playersRef):
				obj = self.scene.addObject("pawn.0"+str(cptr+1))
				parent = self.scene.objects["pawnflag."+str(cptr)]
				obj.scaling = [parent.scaling[0],parent.scaling[0],parent.scaling[0]]
				obj.position = parent.position

		self.clearObjList()
		for cptr,player in enumerate(playersRef):
			self.showNbr(player.score, "playerScoreFlag."+str(cptr))
			self.showNbr(player.nbPawns, "pawnNb."+str(cptr))
		self.showNbr(nbTiles, "nbTileFlag")

	def setPlayer(self, playerNumber):
		self.currentPlayer = playerNumber
		if self.playerFlagObject:
			self.playerFlagObject.endObject()
		self.playerFlagObject = self.scene.addObject("pawn.0"+str(self.currentPlayer+1))
		self.playerFlagObject.position = self.playerFlag.position
		self.playerFlagObject.scaling = [self.playerFlag.scaling[0],self.playerFlag.scaling[0],self.playerFlag.scaling[0]]
