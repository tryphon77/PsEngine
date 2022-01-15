# -*- coding: utf-8 -*-

# mask : functions for handling masks, and several predefined masks


import numpy as np

def mask_or(dest, dest_pos, src, src_pos):
	"""
	Copies (logical or) src mask to dest mask, so as dest_pos and src_pos
	coincides (can be negative)
	"""
	dx, dy = dest_pos
	dh, dw = dest.shape
	sx, sy = src_pos
	sh, sw = src.shape
		
	if dx < 0:
		dx1 = 0
		sx1 = -dx
	else:
		dx1 = dx
		sx1 = 0
	
	if dx + sw > dw:
		dx2 = dw
		sx2 = dw - dx
	else:
		dx2 = dx + sw
		sx2 = sw

	if dy < 0:
		dy1 = 0
		sy1 = -dy
	else:
		dy1 = dy
		sy1 = 0
	
	if dy + sh > dh:
		dy2 = dh
		sy2 = dh - dy 
	else:
		dy2 = dy + sh
		sy2 = sh
	
	dest[dy1:dy2, dx1:dx2] |= src[sy1:sy2, sx1:sx2]


medium_shadow_mask_str = """\
          ************          
       ******************       
    ************************    
   **************************   
  ****************************  
 ****************************** 
********************************
********************************
********************************
********************************
 ****************************** 
  ****************************  
   **************************   
    ************************    
       ******************       
          ************          
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                """

medium_square_shadow_mask_str = """\
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
********************************
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                """

medium_shadow_mask = np.array([[x == '*' for x in row] for row in medium_shadow_mask_str.split('\n')])

local_collision_mask = np.zeros((96, 96), dtype=bool)
