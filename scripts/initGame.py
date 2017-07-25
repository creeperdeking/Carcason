from scripts.game import *
import bge.logic as logic
from scripts.gameEvents import *

def main():
	obj = logic.getCurrentController().owner

	obj["myGame"] = Game(bge.logic.expandPath("//tiles.caconf"), bge.logic.expandPath("//testMap.camap"), bge.logic.expandPath("//defaultStack.caconf"))
	obj["GameEvents"] = GameEvents(obj["myGame"])
	myGame = obj["myGame"]
	"""
	print(myGame.tiles)
	print(myGame.map)
	print(myGame.tileStack)
	myGame.saveMap("/home/kurisu/Documents/Projets/Carcason/testMap.camap")"""
