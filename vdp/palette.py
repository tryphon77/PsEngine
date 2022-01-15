from OpenGL.GL import *
import numpy as np

class Palette():
	def __init__(self, data, cycling = []):
		self.data = data
		datas = [data]
		for _ in cycling:
			data[cycling] = np.roll(data[cycling], 1, axis = 0)
			datas += [data.copy()]
			
		self.ids = []
		for data in datas:
			id_ = glGenTextures(1)
			self.ids += [id_]
			glEnable(GL_TEXTURE_1D)
			glBindTexture(GL_TEXTURE_1D, id_)
			glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA, 256, 0,
						 GL_RGBA, GL_FLOAT, data)
			glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
			
#			print('data = ', self.data)
			print(self)

		self.current_palette = 0
	
	def get_id(self):
		return self.ids[self.current_palette]
	
	def step(self):
		self.current_palette = (self.current_palette + 1) % len(self.ids)
		
	def __repr__(self):
		glEnable(GL_TEXTURE_1D)
		glBindTexture(GL_TEXTURE_1D, self.ids[0])
		temp = glGetTexImage(GL_TEXTURE_1D, 0, GL_RGBA, GL_FLOAT)
		return 'palette %d :\n%s' % (self.ids[0], ', '.join([('%02X%02X%02X%02X') % tuple(muf) for muf in np.array(temp * 256 - .5, 'i')]))