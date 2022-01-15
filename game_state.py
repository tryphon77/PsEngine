# -*- coding: utf-8 -*-

# game_state : singleton, main object

from vdp.vdp import vdp

class GameState:
	def __init__(self):
		self.current_scene = None
	
game_state = GameState()

def update():
	print("GameState.update()")
	if game_state.current_scene:
		game_state.current_scene.update()
	print("/GameState.update()")

def start():
	vdp.set_update_function(update)
	vdp.start()

def set(scene):
	game_state.current_scene = scene
	game_state.current_scene.init()
	
