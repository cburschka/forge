import graphics
import resource
import bas
import sys

def pixelmap(data, scenario):
    bitmap = [[0]*(scenario.outdoor_size[0]*48) for i in range(scenario.outdoor_size[1]*48)]
    floor_colors = {}
    for i in range(scenario.outdoor_size[1]):
        for j in range(scenario.outdoor_size[0]):
            section = scenario.get_outdoor_section(j,i)
            floor_data = section.get_floor_data()
            for k,line in enumerate(floor_data):
                for l,cell in enumerate(line):
                    if cell not in floor_colors:
                        img = graphics.Cell(data.open_sheet(data.defitions['floor'][cell]['which_sheet']), data.defitions['floor'][cell]['which_icon'])
                        floor_colors[cell] = graphics.flooravg(img.read())
                    bitmap[i*48+k][j*48+l] = floor_colors[cell]
    return bitmap

def isomap(data, scenario):
    iso_size = sum(scenario.outdoor_size)*48
    bitmap = [[b'\x00\x00\x00']*(iso_size*23+23) for i in range(iso_size*16+39+9*23)]
    mmx, nnx, mmy, nny = 0,0,0,0
    cx, cy = 48*scenario.outdoor_size[1]-1,0
    ymax = 0
    for i in range(scenario.outdoor_size[1]):
        for j in range(scenario.outdoor_size[0]):
            section = scenario.get_outdoor_section(j,i)
            floor_data = section.get_floor_data()
            height_data = section.get_height_data()
            terrain_data = section.get_terrain_data()
            print("Drawing section {0},{1}".format(i,j))
            on_surface = section.is_on_surface()
            for k,(fl_line,te_line,y_line) in enumerate(zip(floor_data, terrain_data, height_data)):
                for l,(fl_cell,te_cell,y_cell) in enumerate(zip(fl_line,te_line,y_line)):
                    px,py = cx+((j-i)*48+(l-k)), cy+((i+j)*48+(l+k))

                    fl_data = data['floor'][fl_cell]
                    floor_img = data.get_image(fl_data['which_sheet'], fl_data['which_icon'])
                    fpx,fpy = 23*px,16*py-(y_cell-9)*23
                    if floor_img:
                        for y in range(55):
                            for x in range(46):
                                if floor_img[y][x] != b'\xff\xff\xff':
                                    bitmap[fpy+y][fpx+x] = floor_img[y][x]
                    if te_cell:
                        te_data = data['terrain'][te_cell]
                        # AUGH.
                        if 2 <= te_cell <= 73:
                            te_data['which_sheet'] = [614,616][on_surface]

                        terrain_img = data.get_image(te_data['which_sheet'], te_data['which_icon'])
                        tpx,tpy = fpx+te_data['icon_offset_x'],fpy+te_data['icon_offset_y']
                        if terrain_img:
                            for y in range(55):
                                for x in range(46):
                                    if terrain_img[y][x] != b'\xff\xff\xff':
                                        bitmap[tpy+y][tpx+x] = terrain_img[y][x]

                        if 'second_icon' in te_data:
                            terrain_img2 = data.get_image(te_data['which_sheet'], te_data['second_icon'])
                            ttpx,ttpy = fpx+te_data['second_icon_offset_x'],fpy+te_data['second_icon_offset_y']
                            if terrain_img2:
                                for y in range(55):
                                    for x in range(46):
                                        if terrain_img2[y][x] != b'\xff\xff\xff':
                                            bitmap[ttpy+y][ttpx+x] = terrain_img2[y][x]
    return bitmap


def main(maptype, scenario_filename, out_name, scale):
    data = resource.ScenarioData(scenario_filename)
    scenario = bas.Scenario(scenario_filename)
    graphics.Bitmap(maptype(data, scenario)).write(open(out_name, 'wb'), scale)


main(isomap, sys.argv[1], sys.argv[2], int(sys.argv[3]))
