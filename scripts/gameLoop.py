from scripts.game import *
import bge.events as events
import bge.logic as logic

def main():
	if "GameEvents" in logic.getCurrentController().owner:
		logic.getCurrentController().owner["GameEvents"].update()
