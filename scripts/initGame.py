#This script is lauched only one time
from scripts.game import *
import bge.logic as logic
from scripts.gameEvents import *

def main():
	obj = logic.getCurrentController().owner
	#Creating the core game class
	obj["myGame"] = Game(logic.expandPath("//tiles.caconf"), logic.expandPath("//map.camap"), logic.expandPath("//defaultStack.caconf"))
	#Creating an instance to handle the events
	obj["GameEvents"] = GameEvents(obj["myGame"], "map.camap")
	myGame = obj["myGame"]
