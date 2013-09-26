import sheet
import bas
import os
import sys
import re
from binmagic import lint16a, lint32a

DATA_DIR = "/home/christoph/.wine/drive_c/Program Files/Blades of Avernum/Data"
RE_BEGINFLOOR = re.compile('begindefinefloor\s+([0-9]+)\s*;')
RE_FLOORSHEET = re.compile('fl_which_sheet\s*=\s*([0-9]+)\s*;')
RE_FLOORICON = re.compile('fl_which_icon\s*=\s*([0-9]+)\s*;')

def sheet_db(paths):
    DB = {}
    RE_SHEETNAME = re.compile('G([0-9]+)\.BMP')
    for path in paths:
        for path,dirs,files in os.walk(path):
            for filename in files:
                m = RE_SHEETNAME.match(filename.upper())
                if m:
                    DB[int(m.group(1))] = path + '/' + filename
#    print(sorted(DB.keys()))
    return DB
                
def readfloors(scripts):
    floors = {}
    for filename in scripts:
        data = open(filename).read().splitlines()
        floor, floorsheet, flooricon = 0,0,0
        for line in data:
            m = [RE_BEGINFLOOR.search(line), RE_FLOORSHEET.search(line), RE_FLOORICON.search(line)]
            if m[0]:
                floor = int(m[0].group(1))
                floors[floor] = [floorsheet, flooricon]
            elif m[1]:
                floors[floor][0] = floorsheet = int(m[1].group(1))
            elif m[2]:
                floors[floor][1] = flooricon = int(m[2].group(1))
    #print(sorted(floors.keys()))
    return floors
       
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

def bmp(f, data):
    rowsize = (24*len(data[0])+31)//32 * 4
    datasize = rowsize*len(data)
    f.write(b'BM')
    f.write(lint32a(datasize+54))
    f.write(bytes([0]*4))
    f.write(lint32a(54))
    f.write(lint32a(40))
    f.write(lint32a(len(data[0])))
    f.write(lint32a(len(data)))
    f.write(lint16a(1))
    f.write(lint16a(24))
    f.write(lint32a(0))
    f.write(lint32a(datasize))
    f.write(lint32a(2850))
    f.write(lint32a(2850))
    f.write(lint32a(0))
    f.write(lint32a(0))
    pad = bytes([0]*(rowsize - 3*len(data[0])))
    
    for row in data[::-1]:
        for cell in row:
            f.write(bytes(cell))
        f.write(pad)
    f.close()

def main(scenario_filename, out_name):
    SCEN_DIR = os.path.dirname(scenario_filename)
    SCEN_NAME = os.path.basename(scenario_filename)[:-4]
    SCEN_SCRIPT = SCEN_DIR + '/' + SCEN_NAME + 'data.txt'
    db = sheet_db([DATA_DIR, SCEN_DIR])
    floors = readfloors([DATA_DIR + '/corescendata.txt', SCEN_SCRIPT])
    scenario = bas.Scenario(scenario_filename)
    bitmap = [[0]*(scenario.outdoor_size[0]*48) for i in range(scenario.outdoor_size[1]*48)]
    for i in range(scenario.outdoor_size[1]):
        for j in range(scenario.outdoor_size[0]):
            section = scenario.get_outdoor_section(j,i)
#            print(section.name)
            floor_data = section.get_floor_data()
            for k,line in enumerate(floor_data):
                for l,cell in enumerate(line):
                    if cell not in floors:
#                        print("Warning, empty floor",cell)
                        floors[cell] = (0,0,0)
                    if type(floors[cell]) is list:
                        if type(db[floors[cell][0]]) is str:
                            db[floors[cell][0]] = sheet.Sheet(db[floors[cell][0]])
                        floors[cell] = flooravg(sheet.Cell(db[floors[cell][0]], floors[cell][1]).read())
                    bitmap[i*48+k][j*48+l] = floors[cell]
    bmp(open(out_name, 'wb'), bitmap)

main(sys.argv[1], sys.argv[2])
