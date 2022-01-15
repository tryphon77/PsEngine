from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.GL import *
# from OpenGL.GL import glBindTexture, glEnableClientState, glVertexPointer, \
# 					  glTexCoordPointer, glDrawArrays, glDisableClientState, \
# 					  GL_TEXTURE_1D, GL_VERTEX_ARRAY, GL_FLOAT, GL_QUADS, \
# 					  GL_TEXTURE_COORD_ARRAY

import numpy as np

from time import sleep

class Layer():
	def __init__(self, data, palette, start_pos = (0, 0), tile_size = (32, 32), color = (1.0, 1.0, 1.0, 1.0)):
		if False:
			print("Layer")
			print("data: %s" % data)
			print("palette: %s" % palette)
			print('tile_size: %s' % (tile_size,))
		self.palette = palette
		self.color_modifier = color
		
		vbo_data = []
		x, y = start_pos
		w, h = tile_size

		for row in data:
			for tile in row:
				if tile:
					pattern, h_flip, v_flip = tile
					u0, v0, u1, v1 = pattern.get_texcoords(h_flip, v_flip)
					w, h = pattern.get_dims()
					vbo_data += [(x, y, 0, u0, v0),
								 (x + w, y, 0, u1, v0),
								 (x + w, y + h, 0, u1, v1),
								 (x, y + h, 0, u0, v1)]
				x += w
			x = 0
			y += h
		
		self.vbo = vbo.VBO(np.array(vbo_data, dtype=np.float32))
		
		self.sprites = []
		self.sprites_vbo = vbo.VBO(np.array([0., 0., 0., 0., 0.] * 4 * 1024, dtype=np.float32))
		
		self.set_pos(0, 0)
		
		self.offset_uniform_loc = None
		self.color_uniform_loc = None

	def get_pos(self):
		return self.x, self.y

	def set_pos(self, x, y):
		self.x = x
		self.y = y

	def attach_sprites(self, sprites):
		self.sprites += sprites
	
	def remove_all_sprites(self):
		for sprite in self.sprites:
			sprite.disactive()
		self.sprites = []

	def get_palette_id(self):
		return self.palette.get_id()
	
	def get_sprites(self):
		return self.sprites
	
	def update(self):
#		print("Layer.update()")
		ptr = 0
		for sprite in self.sprites:
			if sprite.is_active:
				sprite.update()
				if sprite.needs_update:
					self.sprites_vbo[ptr : ptr + 20] = sprite.get_vbo_data()
#					print("VBO[%d : %d] = %s" % (ptr, ptr + 20, sprite.get_vbo_data()))
					ptr += 20
#		print("/Layer.update()")
	
	def draw(self):
#		print("Layer.draw()")
#		print ('drawing', self, 'at', (self.x, self.y))
		shaders.glUniform2f(self.offset_uniform_loc, self.x, self.y)
		shaders.glUniform4f(self.color_uniform_loc, *self.color_modifier)

		glBindTexture( GL_TEXTURE_1D, self.get_palette_id())

		with self.vbo:
			glEnableClientState(GL_VERTEX_ARRAY)
			glEnableClientState(GL_TEXTURE_COORD_ARRAY)
			glVertexPointer(3, GL_FLOAT, 20, self.vbo)
			glTexCoordPointer(2, GL_FLOAT, 20, self.vbo + 12)

			glDrawArrays(GL_QUADS, 0, len(self.vbo))

		# Draw attached sprites
		with self.sprites_vbo: #.bind()

			if False:
				# print sprite VBO (debug)
				no_of_floats = 5*4*1024
				float_array = (GLfloat * no_of_floats)()
				glGetBufferSubData(GL_ARRAY_BUFFER, 0, no_of_floats * sizeof(GLfloat), float_array)
				print(list(float_array)[:40])	
			
			glVertexPointer(3, GL_FLOAT, 20, self.sprites_vbo)
			glTexCoordPointer(2, GL_FLOAT, 20, self.sprites_vbo + 12)

			ptr = 0
			for sprite in self.sprites:
				if sprite.is_active:
#					print("sprite at (%d, %d) with palette %d" % (sprite.x, sprite.y, sprite.get_palette_id()))
#						print(sprite.palette)
					glActiveTexture( GL_TEXTURE1 )
					glBindTexture( GL_TEXTURE_1D, sprite.get_palette_id())
					glDrawArrays(GL_QUADS, ptr, 4)
				ptr += 4
	
		glDisableClientState(GL_TEXTURE_COORD_ARRAY)
		glDisableClientState(GL_VERTEX_ARRAY)
#		print("/Layer.draw()")
