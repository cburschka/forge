from gi.repository import Gtk, GdkPixbuf

import data.resource as resource
import data.bas as bas

MARGINS = (0, 39+23*4, 0, 23*4)

class IsoTile:
    def __init__(self, pixbuf, dimension, real_size, margin):
        self.pixbuf = pixbuf
        self.dimension = dimension
        self.real_size = real_size
        self.margin = margin

    '''Size in floor tiles, not pixels.'''
    def new(size):
        iso_size = size[0] + size[1]
        map_size = iso_size*23+MARGINS[0]+MARGINS[2], iso_size*16+MARGINS[1]+MARGINS[3]
        return IsoTile(GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, map_size[0], map_size[1]), size, map_size, MARGINS)

    def rescale(self, scale, rough=False):
        interpolation = [GdkPixbuf.InterpType.BILINEAR, GdkPixbuf.InterpType.NEAREST][rough]
        img = self.pixbuf.scale_simple(self.real_size[0]*scale, self.real_size[1]*scale, interpolation)
        rs = self.real_size[0]*scale, self.real_size[1]*scale
        ma = self.margin[0]*scale, self.margin[1]*scale, self.margin[2]*scale, self.margin[3]*scale
        return IsoTile(img, self.dimension, rs, ma)

'''Basically copy_area with transparency.
- source, destination are Pixbuf objects
- position is the coordinate pair on the canvas
- rect is the crop area on the source.'''
def sprite(source, destination, position, rect=None):
    # Copy whole image by default
    rect = rect or (0, 0, source.get_width(), source.get_height())
    source.composite(destination, position[0], position[1], rect[2], rect[3], position[0]-rect[0], position[1]-rect[1], 1, 1, GdkPixbuf.InterpType.NEAREST, 255)

def isomap_outdoor(section, data):
    tile = IsoTile.new((48,48))
    cx, cy = 47,0 # 23x16 slot for the NW corner of the map.
    floor_data = section.get_floor_data()
    height_data = section.get_height_data()
    terrain_data = section.get_terrain_data()
    on_surface = section.is_on_surface()

    # For all spaces in the 48x48 grid.
    for k,(fl_line,te_line,y_line) in enumerate(zip(floor_data, terrain_data, height_data)):
        for l,(fl_cell,te_cell,y_cell) in enumerate(zip(fl_line,te_line,y_line)):
            # 23x16 slot for the current cell
            px,py = cx+l-k, cy+l+k

            fl_data = data['floor'][fl_cell]
            floor_img = data.load_sheet(fl_data['which_sheet'])
            fpx,fpy = MARGINS[0]+23*px,MARGINS[1]+16*py-(y_cell-9)*23
            if floor_img:
                sprite(floor_img, tile.pixbuf, (fpx, fpy), data.find_icon(fl_data['which_sheet'], fl_data['which_icon']))

            if te_cell and te_cell in data['terrain']:
                te_data = data['terrain'][te_cell]
                # AUGH
                if 2 <= te_cell <= 73:
                    # wall graphic variant is specified in the sector data.
                    te_data['which_sheet'] = [614,616][on_surface]
                    
                # AAAAAUGH
                terrain_img = data.load_sheet(te_data['which_sheet'])
                tpx,tpy = fpx+te_data['icon_offset_x'],fpy+te_data['icon_offset_y']
                if 2 <= te_cell <= 9 or 42 <= te_cell <= 45:
                    # TODO: put the corner wall drawing code here once I figure it out.
                    pass

                if terrain_img:
                    sprite(terrain_img, tile.pixbuf, (tpx, tpy), data.find_icon(te_data['which_sheet'], te_data['which_icon']))
                    if 'second_icon' in te_data:
                        ttpx,ttpy = fpx+te_data['second_icon_offset_x'],fpy+te_data['second_icon_offset_y']
                        sprite(terrain_img, tile.pixbuf, (ttpx, ttpy), data.find_icon(te_data['which_sheet'], te_data['second_icon']))
    return tile

class OutdoorMap:
    def __init__(self, tiles, sample=None):
        self.tiles = tiles
        self.sample = sample or self.tiles[0][0]
        self.size = len(self.tiles[0]), len(self.tiles)
        # The tiles overlap, so that the margin is only counted once.
        self.virtual_size = (
            (self.size[0]+self.size[1])*0.5*self.tile_width()+self.margin_x(),
            (self.size[0]+self.size[1])*0.5*self.tile_height()+self.margin_y()
        )

    def generate(scenario, data):
        iso_size = sum(scenario.outdoor_size) * 48
        tiles = [[None]*scenario.outdoor_size[0] for i in range(scenario.outdoor_size[1])]
        for i in range(scenario.outdoor_size[1]):
            for j in range(scenario.outdoor_size[0]):
                tiles[i][j] = isomap_outdoor(scenario.get_outdoor_section(j,i), data)
        return OutdoorMap(tiles)
    
    def rescale(self, scale):
        scaled_tiles = [[None]*self.size[0] for i in range(self.size[1])]
        for i,row in enumerate(self.tiles):
            for j,sector in enumerate(row):
                scaled_tiles[i][j] = sector.rescale(scale)
        return OutdoorMap(scaled_tiles)
    
    def fast_rescale(self, scale, canvas_half, view):
        scaled_tiles = [[None]*self.size[0] for i in range(self.size[1])]
        for i,row in enumerate(self.tiles):
            for j,sector in enumerate(row):
                if not sector:
                    continue
                src, dest = self._crop_sector((i, j), sector, canvas_half, view)
                if src[2] > 0 and src[3] > 0:
                    scaled_tiles[i][j] = sector.rescale(scale, rough=True)
                    sample = scaled_tiles[i][j]
        return OutdoorMap(scaled_tiles, sample=sample)
    
    # view: Coordinates on the scaled virtual map that ought to be centered.
    def blit_to(self, target, view):
        canvas_half = (target.get_width()/2, target.get_height()/2)
        for i,row in enumerate(self.tiles):
            for j,sector in enumerate(row):
                if not sector:
                    continue
                src, dest = self._crop_sector((i, j), sector, canvas_half, view)
                if src[2] > 0 and src[3] > 0:
                    sprite(sector.pixbuf, target, dest, src)

    # Calculate canvas position and crop rectangle for a particular tile.
    def _crop_sector(self, dim, sector, canvas_half, view):
        gridpos = (self.size[1]-1+dim[1]-dim[0]), (dim[1]+dim[0])
        # Coordinates on canvas, relative to center:
        dest = [int(gridpos[0]*self.tile_width()*0.5-view[0]-self.virtual_width()/2),
                int(gridpos[1]*self.tile_height()*0.5-view[1]-self.virtual_height()/2)]
        src = [0, 0, sector.real_size[0], sector.real_size[1]]
                
        if dest[0] < -canvas_half[0]:         # Crop left
            src[0] = -dest[0]-canvas_half[0]
            dest[0] = -canvas_half[0]
        if dest[1] < -canvas_half[1]:         # Crop top
            src[1] = -dest[1]-canvas_half[1]
            dest[1] = -canvas_half[1]
        if dest[0] + src[2] - src[0] > canvas_half[0]: # Crop right
            src[2] = canvas_half[0] - dest[0] + src[0]
        if dest[1] + src[3] - src[1] > canvas_half[1]: # Crop bottom
            src[3] = canvas_half[1] - dest[1] + src[1]
        src[2], src[3] = src[2]-src[0], src[3]-src[1]
        dest = dest[0]+canvas_half[0], dest[1]+canvas_half[1]

        return src, dest

    def virtual_width(self):
        return self.virtual_size[0]
    def virtual_height(self):
        return self.virtual_size[1]
    def tile_width(self):
        return self.sample.real_size[0]-self.margin_x()
    def tile_height(self):
        return self.sample.real_size[1]-self.margin_y()
    def margin_x(self):
        return self.sample.margin[0] + self.sample.margin[2]
    def margin_y(self):
        return self.sample.margin[1] + self.sample.margin[3]


    def save(self, filename):
        large = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, self.virtual_width(), self.virtual_height())
        for i,row in enumerate(self.tiles):
            for j,sector in enumerate(row):
                x,y = (self.size[1]-1+j-i), (j+i)
                px,py = x*self.tile_width()*0.5, y*self.tile_height()*0.5
                sprite(sector, large, (px, py))
        large.savev(filename, "png", [], [])

def map_create(scenario_filename):
    data = resource.ScenarioData(scenario_filename)
    scenario = bas.Scenario(scenario_filename)
    return OutdoorMap.generate(scenario, data)

def map_save(map_surface, out_name):
    pygame.image.save(map_surface, out_name)


def map_view(map_surface):
    size = 800,600
    screen = pygame.display.set_mode(size)
    refresh = True
    motion = False
    view = [(map_surface.get_width() - size[0])//2, (map_surface.get_height()-size[1])//2]
    while 1:
        if refresh:
            screen.fill((0,0,0))
            map_surface.blit_to(screen, view)
            #screen.blit(map_surface, (0,0), view)
            pygame.display.flip()
            refresh = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                motion = True
            elif motion and event.type == pygame.MOUSEMOTION:
                view[0] = max(0, view[0] - event.rel[0])
                view[1] = max(0, view[1] - event.rel[-1])
                refresh = True
            elif event.type == pygame.MOUSEBUTTONUP:
                motion = False


