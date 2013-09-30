import avernumscript
import os, re
from gi.repository.GdkPixbuf import Pixbuf

CNF_FILE = os.environ['HOME'] + '/.forge/forge.ini'
DATA_DIR = open(CNF_FILE).read()[6:] + '/Data'

class ScenarioData:
    def __init__(self, filename):
        self.scen_dir = os.path.dirname(filename)
        self.scen_name = os.path.basename(filename)[:-4]
        self._find_sheets([DATA_DIR, self.scen_dir])

        self.data = avernumscript.ScriptData()
        self.data.readFile(DATA_DIR + '/corescendata.txt')
        self.data.readFile(DATA_DIR + '/corescendata2.txt')
        self.data.readFile(self.scen_dir + '/' + self.scen_name + 'data.txt')
        self.sheets = {}
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

    def __getitem__(self, key):
        return self.data[key]

    def load_sheet(self, n):
        if n in self.sheet_path:
            if n not in self.sheets:
                self.sheets[n] = Pixbuf.new_from_file(self.sheet_path[n]).add_alpha(True, 255, 255, 255)
            return self.sheets[n]

        
    def find_icon(self, sheet, icon):
        # xy position on the grid: rows of ten
        x,y = icon % 10, icon // 10
        # xy bottom-left pixel: note the 1px black borders between.
        rect = (1 + x*47, 1 + y*56, 46, 55)
        if rect[0]+46 > self.sheets[sheet].get_width() or rect[1]+55 > self.sheets[sheet].get_height():
            raise IndexError("Sheet {0} is too small to contain icon #{1}".format(sheet, icon))
        return rect

