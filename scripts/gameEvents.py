"""
Copyright © <01/08/2017>, <Alexis Gros>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
Except as contained in this notice, the name of the <copyright holders> shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the <copyright holders>.
"""


from scripts.game import *
import bge.events as events
import bge.logic as logic
import bge.render as render

#If the mouse is pressed:
def isPressedM(event):
	return logic.KX_INPUT_JUST_ACTIVATED in logic.mouse.inputs[event].queue
#If the keyboard is pressed:
def isPressedK(event):
	return logic.KX_INPUT_JUST_ACTIVATED in logic.keyboard.inputs[event].queue
#The same, but triggered every frame if only activated:
def isActivatedM(event):
	return logic.KX_INPUT_ACTIVE in logic.mouse.inputs[event].status
def isActivatedK(event):
	return logic.KX_INPUT_ACTIVE in logic.keyboard.inputs[event].status

#The GameEvents class handle the events from the player, and then trigger action in the core game class
class GameEvents:
	def __init__(self, game, savingPath):
		self.mouse = logic.mouse
		self.keyboard = logic.keyboard
		self.scene = logic.getCurrentScene()

		#An instance of the core game class:
		self.game = game
		self.savingPath = savingPath
		#The orthographic scale of the camera
		self.orthoScale = 8

		self.baseTile = self.scene.objects["tile"]
		#The cam tracer is the object used to manipulate the position of the camera
		self.camTracer = self.game.camTracer

		logic.mouse.position = (0.5,0.5)

	def update(self):
		# Mouse events:
		mousePosX,mousePosY = logic.mouse.position

		if mousePosX >= 1:
			mousePosX = 1
			self.camTracer.applyMovement((.15, 0, 0), True)
		elif mousePosX <= 0:
			mousePosX = 0
			self.camTracer.applyMovement((-.15, 0, 0), True)
		if mousePosY <= 0:
			mousePosY = 0
			self.camTracer.applyMovement((0, .15, 0), True)
		elif mousePosY >= 1:
			mousePosY = 1
			self.camTracer.applyMovement((0, -.15, 0), True)

		# Update the screen with the current position of the mouse on the board
		tilePos = [0, 0]
		tilePos[0] = round(self.camTracer.position[0] + mousePosX*self.orthoScale-self.orthoScale/2, 0)
		tilePos[1] = round(self.camTracer.position[1] + ((1-mousePosY)*self.orthoScale-self.orthoScale/2)*(render.getWindowHeight() / render.getWindowWidth()), 0)
		self.game.updateCurrentTileView(Position(tilePos))

		if isPressedM(events.LEFTMOUSE):
			self.game.putTile(Position(tilePos))

		# Keyboard events:
		# For putting pawns:
		if self.game.tilePut:
			side = -1
			if isPressedK(events.ZKEY):
				side = 0
			elif isPressedK(events.QKEY):
				side = 1
			elif isPressedK(events.DKEY):
				side = 3
			elif isPressedK(events.SKEY):
				side = 2
			elif isPressedK(events.LEFTCTRLKEY):
				side = 4
			elif isPressedK(events.AKEY):
				side = 5
			elif isPressedK(events.WKEY):
				side = 6
			elif isPressedK(events.CKEY):
				side = 7
			elif isPressedK(events.EKEY):
				side = 8

			if side > -1:
				value = 1
				if isActivatedK(events.LEFTSHIFTKEY):
					value = 2
				if side > 4:
					self.game.putPawn(Element("field", [side]), value)
				for element in self.game.currentTile.elements:
					if side in element.sides:
						self.game.putPawn(element,value)

		if isActivatedK(events.LEFTCTRLKEY):
			if isPressedK(events.SKEY):
				self.game.map.saveMap(bge.logic.expandPath("//"+self.savingPath))
				print("Map saved!")

			if isPressedK(events.TKEY):
				self.game.countFieldsPoints()
			if isPressedK(events.QKEY):
				self.game.endGame()

		if isPressedK(events.SPACEKEY) and self.game.tilePut == False:
			self.game.rotateTile(1)

		if isPressedK(events.VKEY):
			self.game.map.showLinks = loopInt(self.game.map.showLinks+1, 1)

		#Start a new turn:
		if isPressedK(events.SPACEKEY):
			if self.game.tilePut:
				self.game.countPoints()
				for player in self.game.players:
					print(player.name, ":", player.score)
				# We have to find a winner:
				if self.game.nextTurn() == False:
					self.game.map.countFieldsPoints()
					self.game.endGame()
