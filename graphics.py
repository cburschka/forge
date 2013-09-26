import sys
from binmagic import lint32, lint16
    
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
        if self.colordepth not in 8,24:
            self.error("Unsupported color depth (must be 8 or 24).")
        self.rowsize = ((self.colordepth*self.width+31) // 32)*4
        if not self.read32() == 0:
            self.error("Picture must not be compressed.")
        self.file.seek(0x2e)
        if not self.read32() == 256:
            self.error("Not using full color table.")
        self.file.seek(0x36)
        
        if self.colordepth == 8:
            self.colors = []
            for i in range(256):
                self.colors.append(tuple(self.file.read(4)[:3]))

    # pixel value: x,y coordinate
    def __get__(self, c):
        if self.colordepth == 8:
            self.file.seek(self.offset + self.rowsize*c[0] + c[1])
            return self.colors[self.file.read(1)[0]]
        else:
            self.file.seek(self.offset + self.rowsize*c[0] + c[1]*3)
            return tuple(self.file.read(3))
        
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
                out.append([(c[i],c[i+1],c[i+2]) for i in range(0,c,3)])
        return out
 
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


#x = avg(Cell(Sheet(sys.argv[1]), 3).read())
#print(hex((x[0]<<16)+(x[1]<<8)+x[2]))

#print("\n".join("".join(("0"+hex(c)[2:])[-2:] for c in line) for line in Cell(Sheet(sys.argv[1]), 3).read()))
