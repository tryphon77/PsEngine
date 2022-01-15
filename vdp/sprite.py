import numpy as np

log = print

class Sprite():
	def __init__(self, frames, palette, anims = [], visible = False, x = 0, y = 0, frame = 0):
		self.is_active = False
		
		self.palette = palette
		
		self.frames = frames
			
		self.animations = anims
		self.current_animation_id = -1
		self.current_animation = None
		self.current_animation_step = -1
		self.current_tick = -1
		
		self.x = self.y = 0
		self.set_pos(x, y)

		self.current_frame_id = -1
		self.set_frame(frame)

#		self.vbo_data = np.zeros((20,), dtype=np.float32) 
		self.vbo_data = self.current_frame.initial_vbo_data.copy()


	def active(self):
		self.is_active = True
	
	def disactive(self):
		self.is_active = False

	def set_pos(self, x, y):
		if self.x != x or self.y != y:
			self.x = x
			self.y = y
			self.needs_update = True
	
	def get_pos(self):
		return self.x, self.y
	
	def set_frame(self, frame_id):
		log("set_frame: %d" % frame_id)
		if self.current_frame_id != frame_id:
			self.current_frame_id = frame_id
			self.current_frame = self.frames[frame_id]
			self.needs_update = True

	def get_frame(self):
		return self.current_frame

	def set_animation(self, anim_id):
		self.current_animation_id = anim_id
		self.current_animation = self.animations[anim_id]
		self.current_animation_step = -1
		self.current_tick = -1
	
	def get_animation(self):
		return self.current_animation_id

	def get_palette_id(self):
		return self.palette.get_id()

	def get_vbo_data(self):
		print("Sprite.get_vbo_data()")
		frame_data = self.current_frame.initial_vbo_data

		self.vbo_data[::5] = frame_data[::5] + self.x
		self.vbo_data[1::5] = frame_data[1::5] + self.y
		self.vbo_data[2::5] = frame_data[2::5] + self.y
		self.vbo_data[3::5] = frame_data[3::5] + self.y
		self.vbo_data[4::5] = frame_data[4::5] + self.y

		print("/Sprite.get_vbo_data()")
		return self.vbo_data

	def update(self):
		print("Sprite.update()")
		if self.current_animation:
			if self.current_tick < 0:
				self.current_animation_step += 1
				if self.current_animation_step >= len(self.current_animation):
					self.current_animation_step = 0
				
				frame_id, ticks = self.current_animation[self.current_animation_step]
				if frame_id < 0:
					self.current_animation_step -= frame_id
					frame_id, ticks = self.current_animation[self.current_animation_step]
				
				self.current_tick = ticks
				self.set_frame(frame_id)
			
			self.current_tick -= 1
		print("/Sprite.update()")
			
					

class Frame():
	def __init__(self, pos, pattern, hflip=False, vflip=False):
		x, y = pos
		u0, v0, u1, v1 = pattern.get_texcoords(hflip, vflip)
		w, h = pattern.width, pattern.height
		self.initial_vbo_data = np.array([
			-x, -y, 0, u0, v0,
			-x + w, -y, 0, u1, v0,
			-x + w, -y + h, 0, u1, v1,
			-x, -y + h, 0, u0, v1
		], dtype=np.float32)

		