import os
import re
import graphics

DATA_DIR = "/home/christoph/.wine/drive_c/Program Files/Blades of Avernum/Data"

'''Parse AvernumScript'''
class ScriptFile:
    def __init__(self, filename):      
        lines = open(filename).read().splitlines()

        # TODO: Parse actual scripts, not just data definitions.
        RE_EXPR = '(?:(?P<num>-?[0-9]+)|"(?P<str>.*)")'
        RE_STMT = re.compile('\s*(?P<left>[a-z_]+)(?:(?:\s+|\s*=\s*)' + RE_EXPR + ')?\s*;')

        # strip comments
        for line in lines:
            if '//' in line:
                line = line[:line.index('//')]

        statements = []
        for i,line in enumerate(lines):
            m = RE_STMT.match(line)
            if m:
                right = int(m.group('num')) if m.group('num') else m.group('str')
                statements.append((i, m.group('left'), right))
        self.statements = statements


# terminology:
#   "class": creature, floor, terrain, item
#   "type": eg. floor 37
class ScriptData:
    def __init__(self):
        self.definitions = {'creature':{}, 'floor':{}, 'terrain':{}, 'item':{}}

    def error(self, filename, line, msg):
        raise ValueError('Line {1} in {0}: {2}'.format(filename, line, msg))

    def readFile(self, filename):
        scf = ScriptFile(filename)
        RE_DEFINE = re.compile('begindefine(creature|floor|terrain|item)')        
        # we assume that all variables are prefixed with the first two letters of their class
        RE_VAR = re.compile('(cr|fl|te|it)_(.*)')

        # TODO: default values
        defaults = {
          'cr':{}, 
          'fl':{}, 
          'te':{'icon_offset_x':0, 'icon_offset_y':0, 'second_icon_offset_x':0, 'second_icon_offset_y':0},
          'it':{}
        }
        state = {'cr':defaults['cr'].copy(), 'fl':defaults['fl'].copy(), 'te':defaults['te'].copy(), 'it':defaults['it'].copy()}

        for ln,left,right in scf.statements:
            if left == 'clear':
                self.definitions[state['define']][state[state['define']]] = state[state['define'][:2]] = defaults[state['define'][:2]].copy()
            else:
                m = RE_DEFINE.match(left)
                if m:
                    state['define'] = m.group(1)
                    state[m.group(1)] = right
                    # stop editing the previously edited type.
                    state[m.group(1)[:2]] = state[m.group(1)[:2]].copy()
                    # start editing the new type.
                    self.definitions[m.group(1)][right] = state[m.group(1)[:2]]
                else:
                    m = RE_VAR.match(left)
                    if m:
                        # variables can only be set while editing a type of the right class
                        if m.group(1) == state['define'][:2]:
                            # store this value in the state and the currently edited type
                            state[m.group(1)][m.group(2)] = right
                        else:
                            self.error(filename, ln, 'variable {0} assigned while editing {1} #{2}'.format(left, state['define'], state[state['define']]))
                    elif left == 'import':
                        # if the imported type is undefined, set it to default first.
                        if right not in self.definitions[state['define']]:
                            self.definitions[state['define']][right] = defaults[state['define'][:2]].copy()
                            #self.error(filename, ln, 'tried to import undefined {0} #{1} into #{2}'.format(state['define'], right, state[state['define']]))

                        # set both the currently edited type and the state to the previously defined type.
                        self.definitions[state['define']][state[state['define']]] = state[state['define'][:2]] = self.definitions[state['define']][right].copy()

    def __getitem__(self, key):
        return self.definitions[key]

class ScenarioData:
    def __init__(self, filename):
        self.scen_dir = os.path.dirname(filename)
        self.scen_name = os.path.basename(filename)[:-4]
        self._find_sheets([DATA_DIR, self.scen_dir])

        self.data = ScriptData()
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
        
