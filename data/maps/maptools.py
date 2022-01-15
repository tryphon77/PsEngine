import numpy as np
import xml.etree.ElementTree as ET
import os


### TMX loader
def double_tmx(path, base_tiles_dir = ''):

	if base_tiles_dir == '':
		base_tiles_dir = os.path.dirname(path)
		
	def _cvt(data):
		if data[0] == 0 and data[1] == 0 and data[2] == 0 and data[3] == 0:
			return (0, False, False)
		else:
			t_id = data[1] * 0x100 + data[0]
			if t_id in [1, 257, 513, 769]:
				return (0, False, False)
			h_flip = (data[3] & 0x80) != 0
			v_flip = (data[3] & 0x40) != 0
			return (t_id, h_flip, v_flip)

	def _read_attr(e, key, default = ''):
		if key in e.attrib:
			return e.attrib[key]
		return default

	patterns = []
	layers = []
	tex_x = tex_y = 0
	collision_first_gid = 1024

	tree = ET.parse(path)
	root = tree.getroot()
	
	name = _read_attr(root, 'name')
	res = ""
#	 width = _read_attr(root, 'width')
#	 height = _read_attr(root, 'height')
#	 is_toric = _read_attr(root, 'toric', '0')
#	 sprite_layer = _read_attr(root, 'sprite_layer', 0)

	for elt in root:
		if elt.tag == 'tileset':
			first_gid = int(_read_attr(elt, 'firstgid'))
			elt.set('firstgid', str((first_gid - 1)*4 + 1))
			elt.set('tilecount', '1024')
			
			sheet_name = _read_attr(elt[0], 'source')
#				sheets_names += [sheet_name]
		
			print('sheet_name:', sheet_name)
			if True: #not sheet_name.startswith("collision"):
#				bitmap_data, palette_data = load_bmp(sheet_name)
				
				nm, ext = sheet_name.split(".")
				new_sheet_name = "%s-dbl.bmp" % (nm,)
#				new_bitmap_data = bmp_double_size(bitmap_data)
#				save_bmp(new_sheet_name, new_bitmap_data)
				elt[0].set('source', new_sheet_name)
				elt[0].set('width', '1024')
				elt[0].set('height', '1024')

		elif elt.tag == 'layer':
			name = _read_attr(elt, 'name')
			
			if True:
				alpha = float(_read_attr(elt, 'opacity', '1.0')) 
				layer_width = int(_read_attr(elt, 'width'))
				layer_height = int(_read_attr(elt, 'height'))
#				 anim_x = []
#				 anim_y = []

				elt.set('width', str(2*layer_width))
				elt.set('height', str(2*layer_height))

				for elt2 in elt:
					if elt2.tag == 'data':
						data = [[int(x) for x in row.split(',') if x] for row in elt2.text.split()]
						print(layer_height, layer_width, data)
						
						res = [[0] * 2*layer_width for _ in range(2*layer_height)]

						for y in range(layer_height):
							for x in range(layer_width):
								c = data[y][x] - 1
								if c == -1:
									res[2*y][2*x] = '0'
									res[2*y][2*x + 1] = '0'
									res[2*y + 1][2*x] = '0'
									res[2*y + 1][2*x + 1] = '0'
								else:
									cx = c % 16
									cy = c // 16
									c_ = cy*64 + cx*2 + 1
									res[2*y][2*x] = str(c_)
									res[2*y][2*x + 1] = str(c_ + 1)
									res[2*y + 1][2*x] = str(c_ + 32)
									res[2*y + 1][2*x + 1] = str(c_ + 33)
						
						rows = [','.join(row) for row in res]
						elt2.text = '\n' + ',\n'.join(rows) + '\n'
# #						 print '\ndata ='
# #						 print [x for x in decoded_data[:100]]
# 						
# 						if name == "collisions":
# 							collision_data = []
# 							ptr = 0
# 							for _ in range(layer_height):
# 								row = []
# 								for _ in range(layer_width):
# 									t_id, hflip, vflip = _cvt(decoded_data[ptr : ptr + 4])
# 									row += [max(0, t_id - collision_first_gid)]
# 									ptr += 4
# 								collision_data.append(row)

# 						else:
# 							layer_data = []
# 							ptr = 0
# 							for _ in range(layer_height):
# 								row = []
# 								for _ in range(layer_width):
# 									t_id, hflip, vflip = _cvt(decoded_data[ptr : ptr + 4])
# 									row += [(patterns[t_id - 1], hflip, vflip) if t_id >= 1 else 0]
# 									if decoded_data[ptr] != 0:
# 										p_id = decoded_data[ptr + 1]
# 									ptr += 4
# 								layer_data.append(row)
# 							layers.append(Layer(layer_data, palettes[p_id], color = (1.0, 1.0, 1.0, alpha)))
						
#					 elif elt2.tag == 'properties':
#						 for prop in elt2:
#							 name = _read_attr(prop, 'name')
#							 value = _read_attr(prop, 'value')
#							 if name == 'mode':
#								 mode = int(value)
#							 elif name == 'anim_x':
#								 print 'yahoo'
#								 anim_x = eval(value)
#							 elif name == 'anim_y':
#								 print 'yahoo'
#								 anim_y = eval(value)

	tree.write("result.tmx")		
	return

if __name__ == "__main__":
	double_tmx("test.tmx")
