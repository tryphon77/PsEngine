# -*- coding: utf-8 -*-

from interfaces import Event


class EventArea(Event):
	def __init__(self, rect, event_string):
		self.name = "EventArea"
		pass

	def init(self):
		pass

	def get_pos(self):
		return(-1000, -1000)
	
	def update(self):
		pass
