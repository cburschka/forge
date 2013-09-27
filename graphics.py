import sys
from binmagic import lint32, lint16, lint32a, lint16a
    
class Sheet:
    def error(self, msg):
        raise ValueError("Graphics file {0}: {1}".format(self.filename, msg))
        
    def read32(self):
        return lint32(self.file.read(4))
    def read16(self):
        return lint16(self.file.read(2))
        
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'rb')
        if not self.file.read(2) == b'BM':
            self.error("Not a BMP file.")
        self.file.seek(0xa)
        self.offset = self.read32()
        if not self.read32() == 40:
            self.error("Unsupported BMP format version.")
        self.width = self.read32()
        self.height = self.read32()
        if not self.read16() == 1:
            self.error("Number of color planes must be 1.")
        self.colordepth = self.read16()
        if self.colordepth not in (8,24):
            self.error("Unsupported color depth (must be 8 or 24).")
        self.rowsize = ((self.colordepth*self.width+31) // 32)*4
        if not self.read32() == 0:
            self.error("Picture must not be compressed.")
        self.file.seek(0x2e)
        self.colortable = self.read32() or 2**self.colordepth
        self.file.seek(0x36)
        
        if self.colordepth == 8:
            self.colors = []
            for i in range(self.colortable):
                self.colors.append(self.file.read(4)[:3])

    # pixel value: x,y coordinate
    def __get__(self, c):
        if self.colordepth == 8:
            self.file.seek(self.offset + self.rowsize*c[0] + c[1])
            return self.colors[self.file.read(1)[0]]
        else:
            self.file.seek(self.offset + self.rowsize*c[0] + c[1]*3)
            return self.file.read(3)
        
    # rectangle
    def getrect(self, x, y, width, height):
        out = []
        if self.colordepth == 8:
            for i in range(y,y+height):
                self.file.seek(self.offset + self.rowsize*i + x)
                out.append([self.colors[c] for c in self.file.read(width)])
        else:
            for i in range(y,y+height):
                self.file.seek(self.offset + self.rowsize*i + x*3)
                c = self.file.read(width*3)
                out.append([c[i:i+3] for i in range(0,len(c),3)])
        return out[::-1]
 
class Cell:
    def __init__(self, sheet, index):
        self.sheet = sheet
        self.index = index
        # xy position on the grid: rows of ten
        self.grid = (index % 10, index // 10)
        # xy bottom-left pixel: note the 1px black borders between.
        self.position = (1 + self.grid[0] * 47, 1 + self.grid[1] * 56)
        
    def read(self):
        return self.sheet.getrect(self.position[0], self.position[1], 46, 55)

class Bitmap:
    def __init__(self, data):
        self.width = len(data[0])
        self.height = len(data)
        self.data = data

    def write(self, io, scale):
        rowsize = (24*scale*self.width+31)//32 * 4
        datasize = rowsize*self.height
        io.write(b'BM')
        io.write(lint32a(datasize+54))
        io.write(bytes([0]*4))
        io.write(lint32a(54))
        io.write(lint32a(40))
        io.write(lint32a(self.width))
        io.write(lint32a(self.height))
        io.write(lint16a(1))
        io.write(lint16a(24))
        io.write(lint32a(0))
        io.write(lint32a(datasize))
        io.write(lint32a(2850))
        io.write(lint32a(2850))
        io.write(lint32a(0))
        io.write(lint32a(0))
        pad = bytes([0]*(rowsize - 3*self.width*scale))

        tenth = self.height // 10    
        for i in range(len(self.data)-1,-1,-1):
            if i%tenth == 0:
                print("Writing row {0} of {1}".format(self.height-i,self.height))
            for cell in self.data[i]:
                io.write(cell)
            io.write(pad)
        io.close()


#x = avg(Cell(Sheet(sys.argv[1]), 3).read())
#print(hex((x[0]<<16)+(x[1]<<8)+x[2]))

#print("\n".join("".join(("0"+hex(c)[2:])[-2:] for c in line) for line in Cell(Sheet(sys.argv[1]), 3).read()))

def lozenge():
    width = 23
    for y in range(0,16):
        for x in range(width):
            yield (x,y)
            yield (x,-1-y)
            yield (-1-x,y)
            yield (-1-x,-1-y)
        width -= 1 + (y % 2)
        
def flooravg(image):
    R,G,B = 0,0,0
    for x,y in lozenge():
        x,y = x+23,y+16
        r,g,b = image[y][x]
        R,G,B = R+r,G+g,B+b          
    return R//768, G//768, B//768
