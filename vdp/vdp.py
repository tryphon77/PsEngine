
import sys
sys.path.append('./')

import pygame


from OpenGL.GL import *
from OpenGL.arrays import vbo

import numpy as np
from sys import exit

from .constants import * 
from .pattern import Pattern
from .palette import Palette
from .sprite import Sprite, Frame
from .layer import Layer


def ERROR(msg):
	print ('***\n', msg)

class VDP():
	_texture_factor = 1.0
	
	def __init__(self, size = 2048, fps = 60):

		self.fps = fps
		self.init_function = None
		self.update_function = None
		self.close_function = None

		self._init_display()
		self._init_vram(size)
		self._init_shaders()
		
		# init palettes and layers
		self.palettes = []
		self.current_palette = -1
		self.layers = []
				
		self._init_draw()

	def _init_display(self):
		self.screen = pygame.display.set_mode((640, 448), pygame.DOUBLEBUF | pygame.OPENGL)

		glViewport(0, 0, 640, 448)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, 640, 0, 448, -1, 1)
	
		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity()
		
		glEnable (GL_BLEND)
		glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	def _init_vram(self, size):
		self.v_texture_size = size
		VDP._texture_factor = 1.0 / float(size)

		initial_data = np.zeros((self.v_texture_size, self.v_texture_size), 'f')

		self.v_texture = glGenTextures(1)
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.v_texture)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.v_texture_size, self.v_texture_size, 0,
					 GL_ALPHA, GL_FLOAT, initial_data)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glActiveTexture(GL_TEXTURE0)

	def _init_shaders(self):
		# shaders
		VERTEX_SHADER = shaders.compileShader("""#version 330
		
		layout(location = 0) in vec4 position;
		uniform vec2 offset ;
		
		void main()
		{
			  gl_FrontColor = gl_Color;
			  gl_TexCoord[0].xy = gl_MultiTexCoord0.xy;
			  gl_Position = vec4((-offset.x + position.x - 320) / 320, (224 + offset.y - position.y)/224, 0.0, 1.0);
		}""", GL_VERTEX_SHADER)
		
		FRAGMENT_SHADER = shaders.compileShader("""#version 330
			layout(binding = 5) uniform sampler2D texture; 
			layout(binding = 6) uniform sampler1D palette;
			uniform vec4 color_modifier;
				
			void main() 
			{ 
				vec2 uv = gl_TexCoord[0].xy; 
				vec4 color = texture2D(texture, uv); 
				gl_FragColor = texture1D(palette, color.a) * color_modifier;
			}""", GL_FRAGMENT_SHADER)
		
		self.shaders_program = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
		
		# uniform variables
		self.offset_uniform_loc = glGetUniformLocation(self.shaders_program, 'offset')
		self.texture_uniform_loc = glGetUniformLocation(self.shaders_program, 'texture' )
		self.palette_uniform_loc = glGetUniformLocation(self.shaders_program, 'palette' )
		self.color_uniform_loc = glGetUniformLocation(self.shaders_program, 'color_modifier' )

	def _init_draw(self):
		self.clock = pygame.time.Clock()

	def get_sprites_from_layer(self, k):
		if k < len(self.layers):
			return self.layers[k].get_sprites()
		return []
	
	def set_update_function(self, f):
		self.update_function = f
	
	def set_close_function(self, f):
		self.close_function = f
	
	def update(self):
		if self.update_function is not None:
			self.update_function()
		self.draw()

	def start(self):
		self.joy_state = np.zeros((12,), dtype=bool)
		self.joy_pressed = np.zeros((12,), dtype=bool)
	
		self.movie_mode = False
		
		if self.init_function:
			self.init_function()
			
		self.frame_counter = 0
		while True:
			print("Frame: %d" % self.frame_counter)
			self.frame_counter += 1
			
			old_state = self.joy_state.copy()
			self.joy_pressed[:] = False

			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
					self.close()

				elif event.type == pygame.KEYDOWN: #in [pygame.KEYUP, pygame.KEYDOWN]:
					if event.key == pygame.K_ESCAPE: 
						self.close()
					if event.key == pygame.K_m:
						self.movie_mode = not self.movie_mode
					if self.movie_mode or event.key == pygame.K_p:
						surf = self.take_snapshot()
						pygame.image.save(surf, "snap%03d.png" % self.frame_counter)

					
			keys = pygame.key.get_pressed()
			for k, key in enumerate([
				pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
				pygame.K_q, pygame.K_s, pygame.K_d,
				pygame.K_a, pygame.K_z, pygame.K_e,
				pygame.K_RETURN, pygame.K_SPACE]):
				self.joy_state[k] = keys[key]
			
			self.joy_pressed = np.logical_and( np.logical_not(old_state), self.joy_state)

			self.update()
	
	def close(self):
		if self.close_function:
			self.close_function()
			
		pygame.display.quit()
		sys.exit()
		
	def allocate(self, data, x, y):
		h, w = data.shape
		glBindTexture(GL_TEXTURE_2D, self.v_texture)
		glTexSubImage2D(GL_TEXTURE_2D, 0, x, y, w, h, GL_ALPHA, GL_FLOAT, data)

	def load_patterns(self, data, pos = None, rects = [], grid = False, grid_dims = (32, 32)):
		if pos is None:
			print ('Automatic pattern placement')
			print ('Not yet implemented')
			sys.exit()

		x, y = pos
		h, w = data.shape

		if (not grid) and (not rects):
			rects = [(x, y, w, h)]
		elif grid:
			g_w, g_h = grid_dims
			rects = []
			for j in range(0, h - g_h + 1, g_h):
				for i in range(0, w - g_w + 1, g_w):
					rects += [(x + i, y + j, g_w, g_h)]

		self.allocate(data, *pos)
		
		patterns = []
		for rect in rects:
			pattern = Pattern(rect, self._texture_factor)
			if pattern:
				patterns += [pattern]
			else:
				break
		
		return patterns

	def _config_layer(self, layer):
		layer.offset_uniform_loc = self.offset_uniform_loc
		layer.color_uniform_loc = self.color_uniform_loc

	def attach_layers(self, layers):
		for layer in layers:
			print(layer)
			self._config_layer(layer)
		self.layers += layers
	
	def remove_layer(self, layer):
		self.layers.remove(layer)
	
	def update_layers(self):
		pass
	
	def draw(self):
		print('VDP.draw()')
		self.update_layers()
	
		glClearColor(0.0, 1.0, 0.0, 1.0)
		glClear(GL_COLOR_BUFFER_BIT) # | GL_DEPTH_BUFFER_BIT)
	
#		glEnable( GL_TEXTURE_2D )
		glActiveTexture( GL_TEXTURE0 )
		glBindTexture( GL_TEXTURE_2D, self.v_texture)
	
		glEnable( GL_TEXTURE_1D )
		glActiveTexture( GL_TEXTURE1 )
	
		shaders.glUseProgram(self.shaders_program)
		shaders.glUniform1i(self.texture_uniform_loc, 0)
		shaders.glUniform1i(self.palette_uniform_loc, 1)
		shaders.glUniform2f(self.offset_uniform_loc, 0, 0)
		shaders.glUniform4f(self.color_uniform_loc, 1, 1, 1, 1)
		
		# Draw layers
		for layer in self.layers: #[0:1]:
			layer.draw()

		shaders.glUseProgram( 0 )

		self.wait()	
		pygame.display.flip()
		
		print('/VDP.draw()')

	def wait(self):
		self.clock.tick(self.fps)

	def take_snapshot(self):
		glReadBuffer(GL_FRONT)
		pixels = glReadPixels(0, 0, 640, 448, GL_RGB, GL_UNSIGNED_BYTE)
		
		surf = pygame.image.fromstring(pixels, (640, 448), "RGB", True)
		return surf
		

vdp = VDP(fps=60)
