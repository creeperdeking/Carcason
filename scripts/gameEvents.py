from scripts.game import *
import bge.events as events
import bge.logic as logic
import bge.render as render


def isPressedM(event):
	return logic.KX_INPUT_JUST_ACTIVATED in logic.mouse.inputs[event].queue
def isPressedK(event):
	return logic.KX_INPUT_JUST_ACTIVATED in logic.keyboard.inputs[event].queue
def isActivatedM(event):
	return logic.KX_INPUT_ACTIVE in logic.mouse.inputs[event].status
def isActivatedK(event):
	return logic.KX_INPUT_ACTIVE in logic.keyboard.inputs[event].status

class GameEvents:
	def __init__(self, game):
		self.mouse = logic.mouse
		self.keyboard = logic.keyboard
		self.game = game
		self.scene = logic.getCurrentScene()
		self.orthoScale = 8

		self.baseTile = self.scene.objects["tile"]
		self.camTracer = self.scene.objects["cameraCube"]

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

		tilePos = [0, 0]
		tilePos[0] = round(self.camTracer.position[0] + mousePosX*self.orthoScale-self.orthoScale/2, 0)
		tilePos[1] = round(self.camTracer.position[1] + ((1-mousePosY)*self.orthoScale-self.orthoScale/2)*(render.getWindowHeight() / render.getWindowWidth()), 0)

		self.baseTile.position[0] = tilePos[0]
		self.baseTile.position[1] = tilePos[1]

		self.game.updateTiles(Position(tilePos))

		if isPressedM(events.LEFTMOUSE):
			self.game.putTile(Position(tilePos))

		# Keyboard events:
		if isActivatedK(events.ZKEY):
			self.camTracer.applyMovement((0, .15, 0), True)
		if isActivatedK(events.SKEY):
			self.camTracer.applyMovement((0, -.15, 0), True)
		if isActivatedK(events.QKEY):
			self.camTracer.applyMovement((-.15, 0, 0), True)
		if isActivatedK(events.DKEY):
			self.camTracer.applyMovement((.15, 0, 0), True)

		if isPressedK(events.SKEY) and isActivatedK(events.LEFTCTRLKEY):
			self.game.saveMap("/home/kurisu/Documents/Projets/Carcason/testMap.camap")
			print("Map saved!")

		if isPressedK(events.RKEY):
			self.game.rotateTile()

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
				correctedSide = side
				if not side == 4:
					correctedSide = loopInt(side-self.game.currentTile.rotation, 3)
					print(correctedSide)
				for element in self.game.currentTile.elements:
					sides = self.game.currentTile.elements[element]
					if correctedSide == 4:
						if not sides:
							self.game.putPawn(element, side)
					elif correctedSide in sides:
						self.game.putPawn(element, side)

		#Start a new turn:
		if isPressedK(events.ENTERKEY):
			if self.game.tilePut:
				nbPoints = self.game.countPoints()

				if self.game.nextTurn() == False:
					winner = 0
					for cptr,player in enumerate(self.game.players):
						if player.score > self.game.players[winner].score:
							winner = cptr
					obj = self.scene.addObject("pawn.00"+str(winner))
					obj.scaling *= 9
					obj.position = self.camTracer.position
					obj.position.z = 0
