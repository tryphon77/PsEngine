# -*- coding: utf-8 -*-

from char import Char
from tools.loader import load_bmp

from vdp.constants import *
from vdp.vdp import vdp
from vdp.sprite import Sprite, Frame
from vdp.palette import Palette

import game_state as gs
from misc import sgn
from mask import medium_shadow_mask

class Party(Char):
	def __init__(self):
		self.name = "Party"
		pass
	
	def init(self):		
		s_bitmap, s_palette = load_bmp('data/spritemaps/chars-dbl.bmp')
#		s_bitmap, s_palette = load_bmp('data/spritemaps/chars-test.bmp')
		s_palette[9,:] = [0, 0, 0, 0.75]
		sprite_patterns = vdp.load_patterns(s_bitmap, (0, 1024), grid = True, grid_dims = (64, 64))

		hotspot = (31, 63)
		self.sprite = Sprite([
			Frame(hotspot, sprite_patterns[0]),
			Frame(hotspot, sprite_patterns[1]),
			Frame(hotspot, sprite_patterns[1], hflip=True),
			Frame(hotspot, sprite_patterns[2]),
			Frame(hotspot, sprite_patterns[3]),
			Frame(hotspot, sprite_patterns[3], hflip=True),
			Frame(hotspot, sprite_patterns[4]),
			Frame(hotspot, sprite_patterns[5]),
			Frame(hotspot, sprite_patterns[6]),
			Frame(hotspot, sprite_patterns[4], hflip=True),
			Frame(hotspot, sprite_patterns[5], hflip=True),
			Frame(hotspot, sprite_patterns[6], hflip=True)
		], Palette(s_palette), anims = [
			[(0, 255)],
			[(9, 255)],
			[(3, 255)],
			[(6, 255)],
			[(0, 8), (1, 8), (0, 8), (2, 8)],
			[(9, 8), (10, 8), (9, 8), (11, 8)],
			[(3, 8), (4, 8), (3, 8), (5, 8)],
			[(6, 8), (7, 8), (6, 8), (8, 8)],
		   ])
			
		map_scene = gs.game_state.current_scene
		map_scene.ground_layer.attach_sprites([self.sprite])
		self.sprite.active()
		
		self.shadow_mask = medium_shadow_mask

		super().init()
	
	def set_pos(self, pos):
		self.sprite.set_pos(*pos)
	
	def get_pos(self):
		return self.sprite.get_pos()
	
	def update(self):
		print("Party.update()")
		x, y = self.get_pos()
		
		dy = 0
		if vdp.joy_state[JOY_UP]:
			dy = -1
		elif vdp.joy_state[JOY_DOWN]:
			dy = 1
		
		dx = 0
		if vdp.joy_state[JOY_LEFT]:
			dx = -1
		elif vdp.joy_state[JOY_RIGHT]:
			dx = 1
		
#		if vdp.joy_pressed[JOY_C]:
#			if gui_layer_visible:
#				close_gui()
#			else:
#				open_gui()
		
		map_scene = gs.game_state.current_scene
		self.update_local_collision_mask(x//32 - 1, y//32 - 1)
		old_x, old_y = x, y
		dx2, dy2 = 2*dx, 2*dy
		dx3, dy3 = 3*dx, 3*dy
		dx4, dy4 = 4*dx, 4*dy
		if dy == 0:
			if dx:
				dx, dy = map_scene.no_collides_at(self, [
					(dx4, 0), (dx3, -1), (dx3, 1),
					(dx3, 0), (dx2, -2), (dx2, 2),
					(dx2, 0), (dx, -3), (dx, 3), 
					(dx, 0)
				])
		else:
			if dx == 0:
				dx, dy = map_scene.no_collides_at(self, [
					(0, dy4), (-1, dy3), (1, dy3),
					(0, dy3), (-2, dy2), (2, dy2), 
					(0, dy2), (-2, dy), (2, dy),
					(0, dy)])
			else:
				dx, dy = map_scene.no_collides_at(self, [
					(dx3, dy3), 
					(dx2, dy2), (dx, dy2), (dx2, dy),
					(dx, dy), (dx, dy2), (dx2, dy),
					(dx4, 0), (0, dy4)
					])

#		for actor in map_scene.actors[1:]:
#			if self.collides(actor, [(dx, dy)]):
#				dx, dy = 0, 0
#				actor.is_collided = True
#				break
		
		x += dx
		y += dy
			
		self.set_pos((x, y))
	
		dx, dy = sgn(x - old_x), sgn(y - old_y)
		anim = [
			[5, 6, 7], 
			[5, -1, 7], 
			[5, 4, 7]
		][dy + 1][dx + 1]
		
		sprite = self.sprite
		if anim == -1:
			if sprite.get_animation() >= 4:
				sprite.set_animation(sprite.get_animation() - 4)
		else:
			if sprite.get_animation() != anim:
				sprite.set_animation(anim)
	 
#		map_scene.set_camera(x, y)
		
#		if gui_layer_visible:
#			gui_layer.update()
		print("/Party.update()")

party = Party()


