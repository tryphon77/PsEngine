# -*- coding: utf-8 -*-

from interfaces import Scene
from tools.loader import load_tmx
from vdp.vdp import vdp
import game_state as gs
import scenes

class TitleScreenScene(Scene):
	def init(self):
		self.is_running = True
		
		layers = load_tmx(vdp, 'data/maps/ps3title.tmx')['layers']
		vdp.attach_layers(layers)
		self.timer = 300

	def update(self):
		self.timer -= 1
		if self.timer == 0:
			gs.set(scenes.ps3_town_dbl_scene)
