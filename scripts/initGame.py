#This script is lauched only one time
from scripts.game import *
import bge.logic as logic
from scripts.gameEvents import *

def main():
	obj = logic.getCurrentController().owner
	#Creating the core game class
	obj["myGame"] = Game(bge.logic.expandPath("//tiles.caconf"), bge.logic.expandPath("//testMap.camap"), bge.logic.expandPath("//defaultStack.caconf"))
	#Creating an instance to handle the events
	obj["GameEvents"] = GameEvents(obj["myGame"], "testMap.camap")
	myGame = obj["myGame"]
