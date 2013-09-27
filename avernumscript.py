import os
import re
import graphics

DATA_DIR = "/home/christoph/.wine/drive_c/Program Files/Blades of Avernum/Data"

class ScenarioData:
    def __init__(self, filename):
        self.scen_dir = os.path.dirname(filename)
        self.scen_name = os.path.basename(filename)[:-4]
        self.scen_script = self.scen_dir + '/' + self.scen_name + 'data.txt'
        self._find_sheets([DATA_DIR, self.scen_dir])
        self._read_floorterrain([DATA_DIR + '/corescendata.txt', DATA_DIR + '/corescendata2.txt', self.scen_script])
        self.floor_images = {}
        self.terrain_images = {}

    def _find_sheets(self, paths):
        self.db = {}
        RE_SHEETNAME = re.compile('G([0-9]+)\.BMP')
        for path in paths:
            for path,dirs,files in os.walk(path):
                for filename in files:
                    m = RE_SHEETNAME.match(filename.upper())
                    if m:
                        self.db[int(m.group(1))] = path + '/' + filename

    def _read_floorterrain(self, scripts):
        self.floors = {}
        self.terrains = {}
        PATTERNS = [re.compile('begindefine(floor|terrain)\s+([0-9]+)\s*;'),
                    re.compile('(fl|te)_which_(sheet|icon)\s*=\s*([0-9]+)\s*;'),
                    re.compile('import\s*=\s*([0-9]+)\s*;')]
        t = 0
        for filename in scripts:
            data = open(filename).read().splitlines()
            c = {'fl':{0:0,'sheet':0,'icon':0,1:self.floors}, 'te':{0:0,'sheet':0,'icon':0,1:self.terrains}}
            for line in data:
                m = [p.search(line) for p in PATTERNS]
                if m[0]:
                    if t:
                        c[t][1][c[t][0]] = [c[t]['sheet'], c[t]['icon']] # save previous
                    t = m[0].group(1)[:2]
                    x = t
                    c[t][0] = int(m[0].group(2))
                elif m[1]:
                    c[m[1].group(1)][m[1].group(2)] = int(m[1].group(3))
                    x = 0
                elif m[2]:
                    imp = int(m[2].group(1))
                    if x:
                        [c[t]['sheet'], c[t]['icon']] = c[t][1][imp] if imp in c[t][1] else [0,0]
        self.floors[c['fl'][0]] = [c['fl']['sheet'], c['fl']['icon']]
        self.terrains[c['te'][0]] = [c['te']['sheet'], c['te']['icon']]

    def get_floor_image(self, floor):
        if not floor or (floor not in self.floors):
            return None
        elif floor not in self.floor_images:
            if type(self.db[self.floors[floor][0]]) is str:
                self.db[self.floors[floor][0]] = graphics.Sheet(self.db[self.floors[floor][0]])
            self.floor_images[floor] = graphics.Cell(self.db[self.floors[floor][0]], self.floors[floor][1]).read()
        return self.floor_images[floor]
        
    def get_terrain_image(self, terrain):
        if not terrain or (terrain not in self.terrains):
            return None
        elif terrain not in self.terrain_images:
            if type(self.db[self.terrains[terrain][0]]) is str:
                self.db[self.terrains[terrain][0]] = graphics.Sheet(self.db[self.terrains[terrain][0]])
            self.terrain_images[terrain] = graphics.Cell(self.db[self.terrains[terrain][0]], self.terrains[terrain][1]).read()
        return self.terrain_images[terrain]
