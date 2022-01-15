# -*- coding: utf-8 -*-


class Log:
	def __init__(self):
		self.output = open("log.txt", "w")
	
	def __call__(self, text, level=0):
		self.output.write("%s\n" % (text,))
	
	def close(self):
		self.output.close()

def print_mask(mask):
	log('\n'.join([''.join([' *'[int(x)] for x in row]) for row in mask]))
	log("============================================")

log = Log()