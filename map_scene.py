# -*- coding: utf-8 -*-


from misc import sgn, clamp, sort_sprites
from mask import local_collision_mask, mask_or
from interfaces import Scene
from vdp.vdp import vdp
from tools.loader import load_bmp, load_tmx
from vdp.palette import Palette

class MapScene(Scene):
	def __init__(self, map_id, actors, pos):
		self.map_id = map_id
		self.actors = actors
		self.pos = pos
	
	def init(self):
		map_data = load_tmx(vdp, "data/maps/%s.tmx" % self.map_id)
		layers = map_data['layers']
		vdp.attach_layers(layers)
		self.layers = layers
		self.ground_layer = self.layers[map_data['ground_layer']]
		self.twidth, self.theight = (map_data['width'], map_data['height'])
		self.width, self.height = self.map_size = (map_data['width']*32, map_data['height']*32)
				
		self.coll_map = map_data['collision_data']
		coll_bmp, _ = load_bmp("data/maps/collisions-dbl.bmp")
		self.coll_mask = []
		h, w = coll_bmp.shape
		for y in range(0, h, 32):
			for x in range(0, w, 32):
				self.coll_mask.append(coll_bmp[y:y + 32, x: x + 32] != 0)		

		s_bitmap, s_palette = load_bmp('data/spritemaps/npcs-dbl.bmp')
#		s_bitmap, s_palette = load_bmp('data/spritemaps/chars-test.bmp')
		s_palette[15,:] = [0, 0, 0, 0.75]
		MapScene.npc_patterns = vdp.load_patterns(s_bitmap, (1024, 1024), grid = True, grid_dims = (64, 64))
		MapScene.npc_palette = Palette(s_palette)

		for actor in self.actors:
			actor.init()
		self.actors[0].set_pos(self.pos)
#		self.set_camera(*self.actors[0].get_pos())

	
	def update(self):
		print("MapScene.update()")
		for actor in self.actors:
			actor.update()

		sort_sprites(self.ground_layer.get_sprites())

		self.set_camera(*self.actors[0].get_pos())

		for layer in self.layers[:4]:
			layer.update()

		print("/MapScene.update()")

	def set_camera(self, x, y):
		x0 = clamp(x - 320, 0, self.width - 640)
		y0 = clamp(y - 224, 0, self.height - 448)
		print(x, y, x0, y0)		

		for layer in self.layers[:4]:
			#			x, y = layer.get_pos()
			layer.set_pos(x0, y0) #(-600, -200)
	
	def no_collides_at(self, actor, offsets):
		x0, y0 = actor.get_pos()
		
		shadow_mask = actor.shadow_mask
		xm, ym = actor.local_collision_pos
		xm, ym = xm*32, ym*32

		local_collision_mask[:,:] = actor.local_collision_mask[:,:]
		
		for other in self.actors:
			if other != actor:
				x1, y1 = other.get_pos()
				if xm <= x1 + 16 and x1 - 16 < xm + 96 and ym <= y1 + 16 and y1 - 16 < ym + 96:
					mask_or(local_collision_mask, (x1 - xm - 16, y1 - ym - 16), other.shadow_mask, (0, 0))
		
		for dx, dy in offsets:
			x, y = (x0&31) + dx, (y0&31) + dy
#			cx, cy = x // 32, y // 32

			if not (local_collision_mask[32 + y - 16 : 32 + y + 16, 32 + x - 16 : 32 + x + 16] & shadow_mask).any():
				return dx, dy
		return 0, 0
