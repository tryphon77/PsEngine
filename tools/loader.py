import numpy as np
import xml.etree.ElementTree as ET
import zlib, base64, os

from vdp.palette import Palette
from vdp.layer import Layer

def load_bmp(path):
	bmp_header = np.dtype(dict(\
		names = ['bitmap_start', 'palette_start', 'width', 'height', 'nb_planes', 'bpp', 'compression'], \
		offsets = [0x0a, 0x0e, 0x12, 0x16, 0x1a, 0x1c, 0x1e], \
		formats = ['<u4', '<u4', '<u4', '<u4', '<u2', '<u2', '<u4']\
		))

	print('loading', path)
	bmp_buffer = np.fromfile(path, dtype = np.uint8)
	
	bmp_header = np.frombuffer(bmp_buffer, dtype = bmp_header, count = 1)

	if bmp_header['bpp'] == 4:
		palette = bmp_buffer[bmp_header['palette_start'][0] + 0x0e : bmp_header['palette_start'][0] + 0x4e]
		palette.shape = (16, 4)
	
		# All colors are opaque (needs to be fixed)
		palette[:,3] = 255
	
		# Color 0 is transparent
	#	print 'set color 0 (%x %x %x %x) to transparent' % tuple(palette[0,:])	
		palette[0,:] = [0, 0, 0, 0] #[0,255,255,255]
	
	#	print 'color 255 = (%02x %02x %02x %02x)' % tuple(palette[255,:])
		
		# Swap R and G channel
		palette[:,::2] = palette[:,2::-2]
	
		raw_bitmap = bmp_buffer[bmp_header['bitmap_start'][0] :]
		raw_bitmap.shape = (bmp_header['height'][0], bmp_header['width'][0]//2)
		
		bitmap = np.zeros((bmp_header['height'][0], bmp_header['width'][0]), dtype=np.uint8)
		bitmap[:, ::2] = raw_bitmap >> 4
		bitmap[:, 1::2] = raw_bitmap & 15
		
		return np.array(bitmap[::-1], 'f') / 255.0, np.array(palette, 'f') / 255.0

	else:
		palette = bmp_buffer[bmp_header['palette_start'][0] + 0x0e : bmp_header['palette_start'][0] + 0x40e]
		palette.shape = (256, 4)
	
		# All colors are opaque (needs to be fixed)
		palette[:,3] = 255
	
		# Color 0 is transparent
	#	print 'set color 0 (%x %x %x %x) to transparent' % tuple(palette[0,:])	
		palette[0,:] = [0, 0, 0, 0] #[0,255,255,255]
	
	#	print 'color 255 = (%02x %02x %02x %02x)' % tuple(palette[255,:])
		
		# Swap R and G channel
		palette[:,::2] = palette[:,2::-2]
	
		bitmap = bmp_buffer[bmp_header['bitmap_start'][0] :]
		bitmap.shape = (bmp_header['height'][0], bmp_header['width'][0])
	
		return np.array(bitmap[::-1], 'f') / 255.0, np.array(palette, 'f') / 255.0


	
### TMX loader
def load_tmx(vdp, path, base_tiles_dir = ''):
	ground_layer = 0	
	collision_data = None

	if base_tiles_dir == '':
		base_tiles_dir = os.path.dirname(path)
		
	def _cvt(data):
		if data[0] == 0 and data[1] == 0 and data[2] == 0 and data[3] == 0:
			return (0, False, False)
		else:
			t_id = data[1] * 0x100 + data[0]
			if (t_id - 1)%1024 == 0:
				return (0, False, False)
			h_flip = (data[3] & 0x80) != 0
			v_flip = (data[3] & 0x40) != 0
			return (t_id, h_flip, v_flip)

	def _read_attr(e, key, default = ''):
		if key in e.attrib:
			return e.attrib[key]
		return default

	def _read_property(e, key, default = ''):
		if e.attrib["name"] == key:
			return e.attrib["value"]
		return default

	palettes = [None] * 10
	patterns = []
	layers = []
	tex_x = tex_y = 0
	collision_first_gid = 1024

	tree = ET.parse(path)
	root = tree.getroot()
	
	name = _read_attr(root, 'name')
	map_width = int(_read_attr(root, 'width'))
	map_height = int(_read_attr(root, 'height'))
#	 is_toric = _read_attr(root, 'toric', '0')
#	 sprite_layer = _read_attr(root, 'sprite_layer', 0)

	for elt in root:
		if elt.tag == 'properties':
			print(elt.keys())
			print(elt[0].keys())
			ground_layer = int(_read_property(elt[0], 'ground_layer', 0))
		elif elt.tag == 'tileset':
			first_gid = int(_read_attr(elt, 'firstgid'))
			sheet_name = _read_attr(elt[0], 'source')
#				sheets_names += [sheet_name]
			
			print('sheet_name:', sheet_name)
			if sheet_name.startswith("collision"):
				collision_first_gid = first_gid
				print("collision_first_gid:", collision_first_gid)

			else:
				bitmap_data, palette_data = load_bmp(os.path.join(base_tiles_dir, sheet_name))
				
				layer_patterns = vdp.load_patterns(bitmap_data, (tex_x, tex_y), grid = True)
	
				tex_x += 1024
				if tex_x >= vdp.v_texture_size:
					tex_x = 0
					tex_y += 1024
				
				patterns[first_gid - 1 : first_gid + len(layer_patterns) - 1] = layer_patterns
				
				current_palette = Palette(palette_data)
				print("add palette")
				palettes[(first_gid - 1) // 1024] = current_palette

		elif elt.tag == 'layer':
			name = _read_attr(elt, 'name')
			
			if True:
				alpha = float(_read_attr(elt, 'opacity', '1.0')) 
				layer_width = int(_read_attr(elt, 'width'))
				layer_height = int(_read_attr(elt, 'height'))
#				 anim_x = []
#				 anim_y = []

				for elt2 in elt:
					if elt2.tag == 'data':
						encoded_data = elt2.text
						decoded_data = bytearray(zlib.decompress(base64.b64decode(encoded_data)))
						print(layer_height, layer_width, len(decoded_data))
						
#						 print '\ndata ='
#						 print [x for x in decoded_data[:100]]
						
						if name == "collisions":
							collision_data = []
							ptr = 0
							for _ in range(layer_height):
								row = []
								for _ in range(layer_width):
									t_id, hflip, vflip = _cvt(decoded_data[ptr : ptr + 4])
									row += [max(0, t_id - collision_first_gid)]
									ptr += 4
								collision_data.append(row)

						else:
							layer_data = []
							ptr = 0
							old_p_id = -1
							for _ in range(layer_height):
								row = []
								for _ in range(layer_width):
									t_id, hflip, vflip = _cvt(decoded_data[ptr : ptr + 4])
									print(t_id)
									row += [(patterns[t_id - 1], hflip, vflip) if t_id >= 1 else 0]
									if decoded_data[ptr] != 0:
										p_id_ = decoded_data[ptr + 1]
										if palettes[p_id_]:
											p_id = p_id_
											#print('p_id=%d [%02X %02X %02X %02X]' % 
											if old_p_id != p_id:
#												print(tuple([p_id, len(palettes)]) + tuple(decoded_data[ptr : ptr + 4]))
												old_p_id = p_id
									ptr += 4
								layer_data.append(row)
							print("append layer: palette_id=%d" % p_id)
							layers.append(Layer(layer_data, palettes[p_id], color = (1.0, 1.0, 1.0, alpha)))
						
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
								
	return {
		"layers": layers, 
		"collision_data": collision_data,
		"width": map_width,
		"height": map_height,
		"ground_layer": ground_layer
		}
