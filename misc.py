# -*- coding: utf-8 -*-

# misc : miscellaneous functions

def sgn(x):
	if x < 0:
		return -1
	if x > 0:
		return 1
	return 0

def clamp(x, a, b):
	if x < a:
		return a
	elif x > b:
		return b
	return x

def sort_sprites(sprites):
	for i in range(len(sprites) - 1):
		if sprites[i].y > sprites[i + 1].y:
			print("switch")
			sprites[i], sprites[i + 1] = sprites[i + 1], sprites[i]
			sprites[i].needs_update = True
			sprites[i + 1].needs_update = True
