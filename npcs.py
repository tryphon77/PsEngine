# -*- coding: utf-8 -*-


import random

from char import Char
from vdp.sprite import Sprite, Frame
from map_scene import MapScene
import game_state as gs
from mask import medium_shadow_mask

class NPC(Char):
	def __init__(self, ptrn_id, name="", pos=(0, 0), move_rect=(0, 0, 0, 0), nervosity=0,  pace = 90, event_string=""):
		self.name = name
		self.pos = pos
		self.commands = event_string
		self.move_rect = move_rect
		self.nervosity = nervosity
		self.pace = pace
		self.timer = 1
		self.ptrn_id = ptrn_id
			
	def init(self):
		ptrn_id = self.ptrn_id
		hotspot = (31, 63)
		self.sprite = Sprite([
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 0]),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 1]),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 1], hflip=True),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 2]),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 3]),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 3], hflip=True),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 4]),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 5]),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 6]),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 4], hflip=True),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 5], hflip=True),
			Frame(hotspot, MapScene.npc_patterns[ptrn_id + 6], hflip=True)
		], MapScene.npc_palette, anims = [
			[(0, 255)], # DOWN
			[(9, 255)], # LEFT
			[(3, 255)], # UP
			[(6, 255)], # RIGHT
			[(0, 8), (1, 8), (0, 8), (2, 8)],
			[(9, 8), (10, 8), (9, 8), (11, 8)],
			[(3, 8), (4, 8), (3, 8), (5, 8)],
			[(6, 8), (7, 8), (6, 8), (8, 8)],
		   ])
			
		map_scene = gs.game_state.current_scene
		map_scene.ground_layer.attach_sprites([self.sprite])
		self.sprite.active()
		
		self.shadow_mask = medium_shadow_mask
		self.set_pos(self.pos)

		super().init()
	
	def set_pos(self, pos):
		self.sprite.set_pos(*pos)
	
	def get_pos(self):
		return self.sprite.get_pos()

	def update(self):
		print("NPC.update()")
		self.timer -= 1
		if self.timer <= 0:
			coin = random.random()
			if coin < self.nervosity:
				self.direction = random.randint(0, 3)
				self.timer = self.pace
				self.sprite.set_animation(self.direction + 4)
			else:
				self.sprite.set_animation(self.sprite.get_animation() & 3)
		
		else:
			map_scene = gs.game_state.current_scene
			x, y = self.get_pos()
			self.update_local_collision_mask(x//32 - 1, y//32 - 1)

			if self.direction == 0:
				dx, dy = map_scene.no_collides_at(self, [
					(0, 2), (0, 1)])
			elif self.direction == 1:
				dx, dy = map_scene.no_collides_at(self, [
					(-2, 0), (-1, 0)])
			
			elif self.direction == 2:
				dx, dy = map_scene.no_collides_at(self, [
					(0, -2), (0, -1)])
			else:
				dx, dy = map_scene.no_collides_at(self, [
					(2, 0), (1, 0)])
			
			x += dx
			y += dy
			x0, y0, w, h = self.move_rect
			if x0 <= x < x0 + w and y0 <= y < y0 + h:
				self.set_pos((x, y))
			else:
				self.sprite.set_animation(self.sprite.get_animation() & 3)				
				
		print("/NPC.update()")

class NPCMan(NPC):
	def __init__(self, name="", pos=(0, 0), move_rect=(0, 0, 0, 0), event_string=""):
		super().__init__(0, name=name, pos=pos, move_rect=move_rect, nervosity=0.01,  pace = 90, event_string=event_string)

class NPCWoman(NPC):
	def __init__(self, name="", pos=(0, 0), move_rect=(0, 0, 0, 0), event_string=""):
		super().__init__(16, name=name, pos=pos, move_rect=move_rect, nervosity=0.01,  pace = 60, event_string=event_string)

class NPCBoy(NPC):
	def __init__(self, name="", pos=(0, 0), move_rect=(0, 0, 0, 0), event_string=""):
		super().__init__(32, name=name, pos=pos, move_rect=move_rect, nervosity=0.05,  pace = 60, event_string=event_string)

class NPCOldMan(NPC):
	def __init__(self, name="", pos=(0, 0), move_rect=(0, 0, 0, 0), event_string=""):
		super().__init__(48, name=name, pos=pos, move_rect=move_rect, nervosity=0.001,  pace = 120, event_string=event_string)
