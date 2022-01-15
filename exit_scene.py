# -*- coding: utf-8 -*-


from vdp.vdp import vdp
from interfaces import Scene

class ExitScene(Scene):
	def init(self):
		vdp.close()
