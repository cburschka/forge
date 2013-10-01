from gi.repository import Gtk, Gdk, GdkPixbuf
import gui.dialogs as dialogs
import render.maps as maps
import cairo

'''The number of pixels to move the map for each key press.'''
SCROLL_SPEED = 20

class MenuBar(Gtk.MenuBar):
    def __init__(self, tree):
        Gtk.MenuBar.__init__(self)
        for title, items in tree:
            menu = Gtk.Menu()
            menu.show()
            for name, handler in items:
                item = Gtk.MenuItem()
                item.set_label(name)
                item.show()
                item.connect('activate', handler)
                menu.append(item)
            item = Gtk.MenuItem()
            item.set_label(title)
            item.set_use_underline(True)
            item.set_submenu(menu)
            item.show()
            self.append(item)

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Forge 0.0.0")
        
        menu_bar = MenuBar([
            ('_File', [
                ('New', self.missing),
                ('Open', self.open_scenario),
                ('Close', self.close_scenario),
                ('Quit', Gtk.main_quit)
            ]),
            ('_Help', [
                ('About', lambda x: dialogs.AboutDialog(self).run()),
            ])
        ])

        vbox = Gtk.VBox(False, 2)
        self.add(vbox)
        vbox.pack_start(menu_bar, False, False, 0)
        
        self.map = None
        self.map_view = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 800,600)
        self.map_view.fill(0x808080ff)
        self.map_area = MapArea(self.map_view)
        self.map_area.set_size_request(800, 600)
        self.map_area.show()
        self.map_area.set_events(self.map_area.get_events()
                      | Gdk.EventMask.BUTTON_RELEASE_MASK
                      | Gdk.EventMask.BUTTON_PRESS_MASK
                      | Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect('key-press-event', self.map_key_pressed)
        self.map_area.connect('button-press-event', self.map_click)
        self.map_area.connect('button-release-event', self.map_release)
        self.map_area.connect('motion-notify-event', self.map_move)
        self.drag = None

        
        vbox.pack_end(self.map_area, False, False, 0)
        self.viewport = [0,0]
        
    def center_view(self):
        self.viewport = [(self.map.get_width() - self.map_view.get_width())//2, (self.map.get_height() - self.map_view.get_height())//2]

    def open_scenario(self, widget, data=None):
        filename = dialogs.OpenScenarioDialog(self).run()
        if filename:
            self.map = maps.map_create(filename)
            self.center_view()
            self.map_view.fill(0x808080ff)
            self.map.blit_to(self.map_view, self.viewport)
            self.map_area.queue_draw()
            
    def close_scenario(self, widget, data=None):
        self.map = None
        self.map_view.fill(0x808080ff)
        self.map_area.queue_draw()

    def missing(self, widget):
        print('Not implemented')
        return True

    # dx, dy: The direction the map should move
    def move_view(self, dx, dy):
        if not self.map:
            return
        self.viewport[0] -= dx
        self.viewport[1] -= dy
        self.map_view.fill(0x808080ff)
        self.map.blit_to(self.map_view, self.viewport)
        self.map_area.queue_draw()

    def map_key_pressed(self, widget, event, data=None):
        if (event.keyval-1) & 0xfffc == 0xff50:
            d = event.keyval & 0x1
            s = event.keyval & 0x2
            self.move_view(d*(1-s)*SPEED, (d^1)*(s-1)*SPEED)
        else:
            print(hex(event.keyval & 0xfffc))
    def map_click(self, widget, event):
        self.drag =  (event.x,event.y)
    def map_release(self, widget, event):
        self.drag =  False
    def map_move(self,widget,event):
        if self.drag:
            self.move_view(event.x-self.drag[0], event.y - self.drag[1])
            self.drag = (event.x, event.y)

class MapArea(Gtk.DrawingArea):
    def __init__(self, source):
        Gtk.DrawingArea.__init__(self)
        self.connect('draw', self._do_expose)
        self.pixbuf = source

    def _do_expose(self, widget, context):
        cr = self.get_property('window').cairo_create()
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgb(1,1,1)
        Gdk.cairo_set_source_pixbuf(context, self.pixbuf, 0, 0)
        context.paint()

