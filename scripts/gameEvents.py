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
		self.camTracer = self.scene.objects["camera"]

	def update(self):
		# Mouse events:
		mousePosX,mousePosY = logic.mouse.position

		if mousePosX > 1:
			mousePosX = 1
		elif mousePosX < 0:
			mousePosX = 0
		if mousePosY > 1:
			mousePosY = 1
		elif mousePosY < 0:
			mousePosY = 0

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
			if isPressedK(events.UPARROWKEY):
				side = 0
			elif isPressedK(events.LEFTARROWKEY):
				side = 1
			elif isPressedK(events.RIGHTARROWKEY):
				side = 3
			elif isPressedK(events.DOWNARROWKEY):
				side = 2
			elif isPressedK(events.RIGHTCTRLKEY):
				side = 4

			if side > -1:
				if not side == 4:
					side = loopInt(side-self.game.currentTile.rotation, 3)

				for element in self.game.currentTile.elements:
					sides = element.sides
					if side == 4:
						if not sides:
							if isActivatedK(events.RIGHTSHIFTKEY):
								self.game.putPawn(element,2)
							else:
								self.game.putPawn(element,1)
					elif side in sides:
						if isActivatedK(events.RIGHTSHIFTKEY):
							self.game.putPawn(element,2)
						else:
							self.game.putPawn(element,1)

		if isActivatedK(events.ZKEY):
			self.camTracer.applyMovement((0, .15, 0), True)
		if isActivatedK(events.SKEY):
			self.camTracer.applyMovement((0, -.15, 0), True)
		if isActivatedK(events.QKEY):
			self.camTracer.applyMovement((-.15, 0, 0), True)
		if isActivatedK(events.DKEY):
			self.camTracer.applyMovement((.15, 0, 0), True)

		if isPressedK(events.SKEY) and isActivatedK(events.LEFTCTRLKEY):
			self.game.saveMap(bge.logic.expandPath("//"+self.savingPath))
			print("Map saved!")

		if isPressedK(events.RKEY):
			self.game.rotateTile()

		#Start a new turn:
		if isPressedK(events.ENTERKEY):
			if self.game.tilePut:
				self.game.countPoints()
				for player in self.game.players:
					print(player.name, ":", player.score)
				# We have to find a winner:
				if self.game.nextTurn() == False:
					winner = 0
					for cptr,player in enumerate(self.game.players):
						if player.score > self.game.players[winner].score:
							winner = cptr
					obj = self.scene.addObject("pawn.00"+str(winner+1))
					obj.scaling *= 9
					obj.position = self.camTracer.position
					obj.position.z = 0
