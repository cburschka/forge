import resource
import bas
import pygame
import sys

def isomap(data, scenario):
    iso_size = sum(scenario.outdoor_size)*48
    bitmap = pygame.Surface((iso_size*23+23, iso_size*16+39+9*23))
    cx, cy = 48*scenario.outdoor_size[1]-1,0 # 23x16 slot for the NW corner of the map.

    # For all sections.
    for i in range(scenario.outdoor_size[1]):
        for j in range(scenario.outdoor_size[0]):
            section = scenario.get_outdoor_section(j,i)
            floor_data = section.get_floor_data()
            height_data = section.get_height_data()
            terrain_data = section.get_terrain_data()
            on_surface = section.is_on_surface()

            # For all spaces in the 48x48 grid.
            for k,(fl_line,te_line,y_line) in enumerate(zip(floor_data, terrain_data, height_data)):
                for l,(fl_cell,te_cell,y_cell) in enumerate(zip(fl_line,te_line,y_line)):
                    # 23x16 slot for the current cell
                    px,py = cx+((j-i)*48+(l-k)), cy+((i+j)*48+(l+k))

                    fl_data = data['floor'][fl_cell]
                    floor_img = data.load_sheet(fl_data['which_sheet'])
                    fpx,fpy = 23*px,16*py-(y_cell-9)*23
                    if floor_img:
                        bitmap.blit(floor_img, (fpx,fpy), data.find_icon(fl_data['which_sheet'], fl_data['which_icon']))

                    if te_cell:
                        te_data = data['terrain'][te_cell]
                        # AUGH.
                        if 2 <= te_cell <= 73:
                            te_data['which_sheet'] = [614,616][on_surface]

                        terrain_img = data.load_sheet(te_data['which_sheet'])
                        tpx,tpy = fpx+te_data['icon_offset_x'],fpy+te_data['icon_offset_y']
                        if terrain_img:
                            bitmap.blit(terrain_img, (tpx, tpy), data.find_icon(te_data['which_sheet'], te_data['which_icon']))

                        if 'second_icon' in te_data:
                            ttpx,ttpy = fpx+te_data['second_icon_offset_x'],fpy+te_data['second_icon_offset_y']
                            if terrain_img:
                                bitmap.blit(terrain_img, (ttpx, ttpy), data.find_icon(te_data['which_sheet'], te_data['second_icon']))
    return bitmap

def map_create(scenario_filename):
    data = resource.ScenarioData(scenario_filename)
    scenario = bas.Scenario(scenario_filename)
    return isomap(data, scenario)

def map_save(map_surface, out_name):
    pygame.image.save(map_surface, out_name)


def map_view(map_surface):
    size = 800,600
    screen = pygame.display.set_mode(size)
    refresh = True
    motion = False
    view = [(map_surface.get_width() - size[0])//2, (map_surface.get_height()-size[1])//2, 800, 600]
    while 1:
        if refresh:
            screen.blit(map_surface, (0,0), view)
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

map_view(map_create(sys.argv[1]))
