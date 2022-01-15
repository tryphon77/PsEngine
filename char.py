# -*- coding: utf-8 -*-

import numpy as np
from interfaces import Event
import game_state as gs

class Char(Event):
	def init(self):
		self.local_collision_mask = np.zeros((96, 96), dtype=bool)
		self.local_collision_pos = (0, 0)
		x, y = self.get_pos()
		self.update_local_collision_mask(x//32 - 1, y//32 - 1)
	
	def update_local_collision_mask(self, x, y):
		map_scene = gs.game_state.current_scene		
		if self.local_collision_pos != (x, y):
	#		log("%s != (%d, %d)" % (local_collision_pos, x, y))
			cj = 0
			x0, y0 = x, y
			for j in range(3):
				ci = 0
				x = x0
				for i in range(3):
					if 0 <= x < map_scene.twidth and 0 <= y < map_scene.theight:
						coll_cell = map_scene.coll_map[y][x]					
						self.local_collision_mask[cj : cj + 32, ci : ci + 32] = map_scene.coll_mask[coll_cell]
					else:
						self.local_collision_mask[cj : cj + 32, ci : ci + 32] = True
						
					x += 1
					ci += 32
				y += 1
				cj += 32
			
			self.local_collision_pos = (x0, y0)
			
	#		log("local_collision_mask at (%d, %d)" % (x0, y0))
	#		print_mask(local_collision_mask)
