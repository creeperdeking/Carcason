from scripts.game import *
import bge.logic as logic
from scripts.gameEvents import *

def main():
	obj = logic.getCurrentController().owner

	obj["myGame"] = Game("/home/kurisu/Documents/Projets/Carcason/tiles.caconf", "/home/kurisu/Documents/Projets/Carcason/testMap.camap", "/home/kurisu/Documents/Projets/Carcason/defaultStack.caconf")
	obj["GameEvents"] = GameEvents(obj["myGame"])
	myGame = obj["myGame"]
	"""
	print(myGame.tiles)
	print(myGame.map)
	print(myGame.tileStack)
	myGame.saveMap("/home/kurisu/Documents/Projets/Carcason/testMap.camap")"""
