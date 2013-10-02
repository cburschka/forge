from gi.repository import Gtk, GdkPixbuf

import data.resource as resource
import data.bas as bas

def isomap_empty(size):
    iso_size = (size[0] + size[1])
    map_size = (iso_size*23+23, iso_size*16+39+20*23*0)
    m = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, map_size[0],map_size[1])
    return m

'''Basically copy_area with transparency.
- source, destination are Pixbuf objects
- position is the coordinate pair on the canvas
- rect is the crop area on the source.'''
def sprite(source, destination, position, rect=None):
    # Copy whole image by default
    rect = rect or (0, 0, source.get_width(), source.get_height())
    source.composite(destination, position[0], position[1], rect[2], rect[3], position[0]-rect[0], position[1]-rect[1], 1, 1, GdkPixbuf.InterpType.NEAREST, 255)

def isomap_outdoor(section, data):
    bitmap = isomap_empty((48,48))
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
            fpx,fpy = 23*px,16*py-(y_cell-9)*23
            if floor_img:
                #floor_img.savev("testcell.png", "png", [], [])
                #return
                sprite(floor_img, bitmap, (fpx, fpy), data.find_icon(fl_data['which_sheet'], fl_data['which_icon']))
                #bitmap.blit(floor_img, (fpx,fpy), )

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
                    sprite(terrain_img, bitmap, (tpx, tpy), data.find_icon(te_data['which_sheet'], te_data['which_icon']))

#                    bitmap.blit(terrain_img, (tpx, tpy), data.find_icon(te_data['which_sheet'], te_data['which_icon']))

                    if 'second_icon' in te_data:
                        ttpx,ttpy = fpx+te_data['second_icon_offset_x'],fpy+te_data['second_icon_offset_y']
                        sprite(terrain_img, bitmap, (ttpx, ttpy), data.find_icon(te_data['which_sheet'], te_data['second_icon']))
    return bitmap

class OutdoorMap:
    def __init__(self, tiles):
        self.tiles = tiles
        self.size = len(self.tiles[0]), len(self.tiles)
        self.virtual_size = (
            (self.size[0]+1)*self.tile_width()*0.5,
            (self.size[1]+1)*self.tile_height()*0.5
        )

    def generate(scenario, data):
        #print(scenario.outdoor_size)
        iso_size = sum(scenario.outdoor_size) * 48
        tiles = [[None]*scenario.outdoor_size[0] for i in range(scenario.outdoor_size[1])]
        # For all sections.
        for i in range(scenario.outdoor_size[1]):
            for j in range(scenario.outdoor_size[0]):
                tiles[i][j] = isomap_outdoor(scenario.get_outdoor_section(j,i), data)
        return OutdoorMap(tiles)
    
    def rescale(self, scale):
        scaled_tiles = [[None]*self.size[0] for i in range(self.size[1])]
        for i,row in enumerate(self.tiles):
            for j,sector in enumerate(row):
                scaled_tiles[i][j] = sector.scale_simple(sector.get_width()*scale, sector.get_height()*scale, GdkPixbuf.InterpType.BILINEAR)
        return OutdoorMap(scaled_tiles)
    
    # view: Coordinates on the scaled virtual map that ought to be centered.
    def blit_to(self, target, view):
        for i,row in enumerate(self.tiles):
            for j,sector in enumerate(row):
                x,y = (self.size[1]-1+j-i), (j+i)
                # Coordinates on canvas:
                px = int(x*self.tile_width()*0.5-view[0]-self.virtual_width()/2)
                py = int(y*self.tile_height()*0.5-view[1]-self.virtual_height()/2)
                #print("Drawing {0} on {1} {2}".format((i,j),(x,y),(px,py)))
                self._project_slice(sector, target, px, py)

    # dest_x, dest_y represent relative position of sector's (0,0)
    # to the center of the virtual canvas.
    def _project_slice(self, sector, dest_buf, dest_x, dest_y):
        src_x, src_y, src_x2, src_y2 = 0, 0, sector.get_width(), sector.get_height()
        canvas_half = (dest_buf.get_width()/2, dest_buf.get_height()/2)
        
        if dest_x < -canvas_half[0]:         # Crop left
            src_x = -dest_x-canvas_half[0]
            dest_x = -canvas_half[0]
        if dest_y < -canvas_half[1]:         # Crop top
            src_y = -dest_y-canvas_half[1]
            dest_y = -canvas_half[1]
        if dest_x + src_x2 > canvas_half[0]: # Crop right
            src_x2 = canvas_half[0] - dest_x
        if dest_y + src_y2 > canvas_half[1]: # Crop bottom
            src_y2 = canvas_half[1] - dest_y
        src_x2, src_y2 = src_x2-src_x, src_y2-src_y
        dest_x, dest_y = dest_x+canvas_half[0], dest_y+canvas_half[1]

        if src_x2 > 0 and src_y2 > 0:
            sprite(sector, dest_buf, (dest_x, dest_y), (src_x, src_y, src_x2, src_y2))

    def virtual_width(self):
        return self.virtual_size[0]
    def virtual_height(self):
        return self.virtual_size[1]
    def tile_width(self):
        return self.tiles[0][0].get_width()
    def tile_height(self):
        return self.tiles[0][0].get_height()

    def save(self, filename):
        large = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, self.get_width(), self.get_height())
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


