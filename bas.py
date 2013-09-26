from binmagic import bint16, str0

SIZE_GLOBAL = 0x1d38
SIZE_OUTDOOR = 0x325c

class Scenario:
    def read16(self):
        return bint16(self.file.read(2))

    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'rb')
        self.file.seek(0xc)
        self.outdoor_size = (self.read16(), self.read16())
    
    def get_outdoor_section(self, x, y):
        n = y * self.outdoor_size[0] + x
        return OutdoorSection(self, n)


class OutdoorSection:
    def __init__(self, scenario, index):
        self.scenario = scenario
        self.index = index
        self.offset = SIZE_GLOBAL + index*SIZE_OUTDOOR
        self.scenario.file.seek(self.offset)
        self.name = str0(self.scenario.file.read(20))
    
    def get_floor_data(self):
        self.scenario.file.seek(self.offset + 0x14)
#        print(hex(self.offset + 0x14))
        data = list(self.scenario.file.read(48 * 48))
        return [[data[48*j+i] for j in range(48)] for i in range(48)]

