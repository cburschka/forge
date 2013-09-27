import avernumscript
import graphics
import os
import re

DATA_DIR = "/home/christoph/.wine/drive_c/Program Files/Blades of Avernum/Data"

class ScenarioData:
    def __init__(self, filename):
        self.scen_dir = os.path.dirname(filename)
        self.scen_name = os.path.basename(filename)[:-4]
        self._find_sheets([DATA_DIR, self.scen_dir])

        self.data = avernumscript.ScriptData()
        self.data.readFile(DATA_DIR + '/corescendata.txt')
        self.data.readFile(DATA_DIR + '/corescendata2.txt')
        self.data.readFile(self.scen_dir + '/' + self.scen_name + 'data.txt')
        self.sheet = {}
        self.img = {}
        
    def _find_sheets(self, paths):
        self.sheet_path = {}
        RE_SHEETNAME = re.compile('G([0-9]+)\.BMP')
        for path in paths:
            for path,dirs,files in os.walk(path):
                for filename in files:
                    m = RE_SHEETNAME.match(filename.upper())
                    if m:
                        self.sheet_path[int(m.group(1))] = path + '/' + filename

    def open_sheet(self, n):
        if n not in self.sheet:
            self.sheet[n] = graphics.Sheet(self.sheet_path[n])
        return self.sheet[n]

    def __getitem__(self, key):
        return self.data[key]
        
    def get_image(self, sheet, icon):
        if sheet not in self.img:
            self.img[sheet] = {}
        if icon not in self.img[sheet]:
            self.img[sheet][icon] = graphics.Cell(self.open_sheet(sheet), icon).read()
        return self.img[sheet][icon]
