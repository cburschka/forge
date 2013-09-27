import graphics
import avernumscript
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
                        floor_colors[cell] = graphics.flooravg(data.get_floor_image(cell))
                    bitmap[i*48+k][j*48+l] = floor_colors[cell]
    return bitmap

def isomap(data, scenario):
    iso_size = sum(scenario.outdoor_size)*48
    bitmap = [[(0,0,0)]*(iso_size*23+23) for i in range(iso_size*16+39)]
    mmx, nnx, mmy, nny = 0,0,0,0
    cx, cy = 48*scenario.outdoor_size[1]-1,0
    for i in range(scenario.outdoor_size[1]):
        for j in range(scenario.outdoor_size[0]):
            section = scenario.get_outdoor_section(j,i)
            floor_data = section.get_floor_data()
            height_data = section.get_height_data()
            terrain_data = section.get_terrain_data()
            for k,(fl_line,te_line,y_line) in enumerate(zip(floor_data, terrain_data, height_data)):
                for l,(fl_cell,te_cell,y_cell) in enumerate(zip(fl_line,te_line,y_line)):
                    floor = data.get_floor_image(fl_cell)
                    terrain = data.get_terrain_image(te_cell)
                    px,py = cx+((j-i)*48+(l-k)), cy+((i+j)*48+(l+k))
                    for y in range(55):
                        for x in range(46):
                            if terrain and terrain[y][x] != (0xff,0xff,0xff):
                                bitmap[16*py+y-(y_cell-9)*23][23*px+x] = terrain[y][x]
                            elif floor and floor[y][x] != (0xff,0xff,0xff):
                                bitmap[16*py+y-(y_cell-9)*23][23*px+x] = floor[y][x]
    return bitmap


def main(maptype, scenario_filename, out_name, scale):
    data = avernumscript.ScenarioData(scenario_filename)
    scenario = bas.Scenario(scenario_filename)
    graphics.Bitmap(maptype(data, scenario)).write(open(out_name, 'wb'), scale)


main(isomap, sys.argv[1], sys.argv[2], int(sys.argv[3]))
