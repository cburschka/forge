import pygame
import os
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GdkX11
import map

def create_menu_tree(title, sub):
    menu = Gtk.Menu()
    for name, handler in sub:
        create_menu_item(name, handler, menu)
    return create_menu(title, menu)

def create_menu(label, menu):
    item = create_menu_item(label, None, None)
    item.set_use_underline(True)
    item.set_submenu(menu)
    item.show()
    return item

def create_menu_item(label, handler = None, menu = None):
    item = Gtk.MenuItem()
    item.set_label(label)
    item.show()
    if handler:
        item.connect("activate", handler)
    if menu:
        menu.append(item)
    return item

class GameWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        vbox = Gtk.VBox(False, 2)
        vbox.show()
        self.add(vbox)

        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        #create the menu
        file_menu = create_menu_tree('_File', [
            ('Open', self.open_scenario),
            ('About', self.show_about),
            ('Quit', self.quit)
        ])
            
        menu_bar = Gtk.MenuBar()
        vbox.pack_start(menu_bar, False, False, 0)
        menu_bar.show()
        menu_bar.append(file_menu)

        #create the drawing area
        da = Gtk.DrawingArea()
        da.set_size_request(800, 600)
        da.show()
        vbox.pack_end(da, False, False, 0)
        da.connect("realize",self._realized)
        self.map = pygame.Surface((1,1)) # empty map
        self.viewport = [0,0,800,600]

        #collect key press events
        self.connect("key-press-event", self.key_pressed)

    def key_pressed(self, widget, event, data=None):
        redraw = True
        if event.keyval == 65361: # <
            self.viewport[0] -= 5
        elif event.keyval == 65362: # ^
            self.viewport[1] -= 5 
        elif event.keyval == 65363: # >
            self.viewport[0] += 5
        elif event.keyval == 65364: # v
            self.viewport[1] += 5
        else:
            redraw = False
        if redraw:
            self.draw()

    def show_about(self, widget, data=None):
	      title = "Forge 0.0.0"
	      dialog = Gtk.Dialog(title, self, Gtk.DialogFlags.MODAL,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
	      content_area = dialog.get_content_area()
	      label = Gtk.Label("Forge is a product of the Ermarian Network, 2013.")
	      link = Gtk.LinkButton("http://github.com/cburschka/forge-python", "http://github.com/cburschka/forge-python")
	      label.show()
	      link.show()
	      content_area.add(label)
	      content_area.add(link)
	      response = dialog.run()
	      dialog.destroy()

    def open_scenario(self, widget, data=None):
        dialog = Gtk.FileChooserDialog("Open Scenario File", self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        bas_filter = Gtk.FileFilter()
        bas_filter.set_name("BoA Scenario Files - *.bas")
        bas_filter.add_pattern("*.bas")
        dialog.add_filter(bas_filter)
        response = dialog.run()
        self.open_file = dialog.get_filename()
        if response == Gtk.ResponseType.OK:
            print("File opened: " + self.open_file)
            
        dialog.destroy()
        self.map = map.map_create(self.open_file)
        self.center_view()
        self.draw()
        
    def center_view(self):
        self.viewport[0:2] = [(self.map.get_width() - self.screen.get_width())//2, (self.map.get_height() - self.screen.get_height())//2]

    def quit(self, widget, data=None):
        self.destroy()

    def draw(self):
        self.screen.blit(self.map, (0,0), self.viewport)
        pygame.display.flip()
        return True

    def _realized(self, widget, data=None):
        os.putenv('SDL_WINDOWID', str(widget.get_window().get_xid()))        
        pygame.init()
        pygame.display.set_mode((800, 600), 0, 0)
        self.screen = pygame.display.get_surface()
        GObject.timeout_add(200, self.draw)

if __name__ == "__main__":
    window = GameWindow()
    window.connect("destroy",Gtk.main_quit)
    window.show()
    Gtk.main()
