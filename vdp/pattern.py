class Pattern():
    def __init__(self, rect, factor):
        x, y, w, h = rect
        self.left, self.right, self.top, self.bottom = \
            float(x) * factor, \
            float(x + w) * factor,\
            float(y + h) * factor, \
            float(y) * factor
        
        self.height, self.width = h, w
        self.tex_height, self.tex_width = h * factor, w * factor

#        print ('dbgpattern at %f, %f, %f, %f' % (self.left, self.bottom, self.right, self.top))

    def get_texcoords(self, h_flip = False, v_flip = False):
        x0 = self.left
        x1 = self.right
        y0 = self.bottom
        y1 = self.top
        if h_flip:
            x0, x1 = x1, x0
        if v_flip:
            y0, y1 = y1, y0
        return (x0, y0, x1, y1)  
    
    def get_dims(self):
        return (self.width, self.height)
