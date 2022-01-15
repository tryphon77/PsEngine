from OpenGL.GL import *
from OpenGL.arrays import vbo

import pygame


def load_bmp(path):
	bmp_header = dtype(dict(\
		names = ['bitmap_start', 'palette_start', 'width', 'height', 'bpp', 'compression'], \
		offsets = [0x0a, 0x0e, 0x12, 0x16, 0x1c, 0x1e], \
		formats = ['<u4', '<u4', '<u4', '<u4', '<u2', '<u4']\
		))

	print('loading', path)
	bmp_buffer = fromfile(path, dtype = uint8)
	
	bmp_header = frombuffer(bmp_buffer, dtype = bmp_header, count = 1)
	
	palette = bmp_buffer[bmp_header['palette_start'][0] + 0x0e : bmp_header['palette_start'][0] + 0x40e]
	palette.shape = (256, 4)

	# All colors are opaque (needs to be fixed)
	palette[:,3] = 255

	# Color 0 is transparent
	palette[0,:] = [0, 0, 0, 0]
	
	# Swap R and G channel
	palette[:,::2] = palette[:,2::-2]

	bitmap = bmp_buffer[bmp_header['bitmap_start'][0] :]
	bitmap.shape = (bmp_header['height'][0], bmp_header['width'][0])

	return ( array(bitmap[::-1], 'f') / 255.0, array(palette, 'f') / 255.0)


screen = pygame.display.set_mode((640, 448), pygame.DOUBLEBUF | pygame.OPENGL)

glViewport(0, 0, 640, 448)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, 640, 0, 448, -1, 1)

glMatrixMode(GL_MODELVIEW);
glLoadIdentity()

glEnable (GL_BLEND)
glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


size = 2048
VDP._texture_factor = 1.0 / float(size)

initial_data = zeros((self.v_texture_size, self.v_texture_size), 'f')

v_texture = glGenTextures(1)
glEnable(GL_TEXTURE_2D)
glBindTexture(GL_TEXTURE_2D, v_texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, size, size, 0,
			 GL_ALPHA, GL_FLOAT, initial_data)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glActiveTexture(GL_TEXTURE0)


# shaders
VERTEX_SHADER = shaders.compileShader("""#version 330

layout(location = 0) in vec4 position;
uniform vec2 offset ;

void main()
{
	  gl_FrontColor = gl_Color;
	  gl_TexCoord[0].xy = gl_MultiTexCoord0.xy;
	  gl_Position = vec4((offset.x + position.x - 320) / 320, (224 - offset.y - position.y)/224, 0.0, 1.0);
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

shaders_program = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)

# uniform variables
offset_uniform_loc = glGetUniformLocation(shaders_program, 'offset')
texture_uniform_loc = glGetUniformLocation(shaders_program, 'texture' )
palette_uniform_loc = glGetUniformLocation(shaders_program, 'palette' )
color_uniform_loc = glGetUniformLocation(shaders_program, 'color_modifier' )


clock = pygame.time.Clock()


