# -*- coding: utf-8 -*-

import numpy as np
import random

from vdp.constants import *
from vdp.vdp import vdp
from vdp.sprite import Frame, Sprite
from vdp.palette import Palette
from vdp.layer import Layer
from tools.loader import load_bmp, load_tmx

from tools.debug import print_mask, log

from mask import mask_or, medium_shadow_mask, local_collision_mask
from misc import sgn, clamp
import game_state as gs
from interfaces import Scene

from exit_scene import ExitScene
import scenes

class SegaLogoScene(Scene):
	def init(self):
		self.is_running = True
		
		layers = load_tmx(vdp, 'data/maps/sega.tmx')['layers']
		vdp.attach_layers(layers)
		self.timer = 300

	def update(self):
		self.timer -= 1
		if self.timer == 0:
			gs.set(scenes.title_screen_scene)
