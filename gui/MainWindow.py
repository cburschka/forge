from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import gui.dialogs as dialogs
import render.maps as maps
import cairo

'''The number of pixels to move the map for each key press.'''
SCROLL_SPEED = 20
ZOOM = [0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.625, 0.75, 1]

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
                ('Save', self.missing),
                ('Export Map', self.export_map),
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
        
        self.map_view = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 800,600)
        self.map_view.fill(0x808080ff)
        self.map_area = MapArea(self.map_view)
        self.map_area.set_size_request(800, 600)
        self.map_area.show()
        self.connect('key-press-event', self.event_key_pressed)
        self.map_area.connect('button-press-event', self.event_map_click)
        self.map_area.connect('button-release-event', self.event_map_release)
        self.map_area.connect('motion-notify-event', self.event_map_move)
        self.map_area.connect('scroll-event', self.event_map_scroll)

        
        vbox.pack_end(self.map_area, False, False, 0)
        self.center_view()
        self.map = None
        self.scaled_map = None
        self.zoom = ZOOM.index(1)
        self.drag = None
        self.refine = False
        GLib.timeout_add_seconds(1, self.refine_map)


    def center_view(self):
        self.view = [0,0]

    def open_scenario(self, widget, data=None):
        filename = dialogs.OpenScenarioDialog(self).run()
        if filename:
            self.map = maps.map_create(filename)
            self.scaled_map = self.map if ZOOM[self.zoom] == 1 else self.map.rescale(ZOOM[self.zoom])
            self.center_view()
            self.redraw_view()
            
    def close_scenario(self, widget, data=None):
        self.map = None
        self.clear_map()

    def clear_map(self):
        self.map_view.fill(0x808080ff)
        self.map_area.queue_draw()        

    def redraw_view(self):
        self.map_view.fill(0x808080ff)
        self.scaled_map.blit_to(self.map_view, self.view)
        self.map_area.queue_draw()
        
    def refine_map(self):
        if self.refine:
            self.scaled_map = self.map.rescale(ZOOM[self.zoom])
            self.refine = False
            self.redraw_view()
        return True

    def rescale_map(self, d=0):
        # Scaled map is always smaller. This will produce a result faster.
        self.scaled_map = self.scaled_map.rescale(ZOOM[self.zoom+d]/ZOOM[self.zoom])
        self.zoom += d
        self.refine = True
        self.redraw_view()

    def export_map(self, widget, data=None):
        filename = dialogs.SaveMapDialog(self).run()
        if filename:
            self.scaled_map.save(filename)

    def missing(self, widget):
        print('Not implemented')
        return True

    # dx, dy: The direction the map should move
    def move_view(self, dx, dy):
        if not self.scaled_map:
            return
        self.view[0] -= dx
        self.view[1] -= dy
        self.map_view.fill(0x808080ff)
        self.redraw_view()

    def rezoom(self, d):
        if 0 <= self.zoom + d < len(ZOOM):
            self.rescale_map(d)

    def event_key_pressed(self, widget, event, data=None):
        if (event.keyval-1) & 0xfffc == 0xff50:
            d = event.keyval & 0x1
            s = event.keyval & 0x2
            self.move_view(d*(1-s)*SPEED, (d^1)*(s-1)*SPEED)
            return True
        else:
            return False
    def event_map_click(self, widget, event):
        self.drag =  (event.x,event.y)
        return True
    def event_map_release(self, widget, event):
        self.drag =  False
        return True
    def event_map_move(self, widget, event):
        if self.drag:
            self.move_view(event.x-self.drag[0], event.y - self.drag[1])
            self.drag = (event.x, event.y)
        return True
    def event_map_scroll(self, widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            self.rezoom(1)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.rezoom(-1)


class MapArea(Gtk.DrawingArea):
    def __init__(self, source):
        Gtk.DrawingArea.__init__(self)
        self.connect('draw', self._do_expose)
        self.pixbuf = source
        self.set_events(self.get_events()
                      | Gdk.EventMask.BUTTON_RELEASE_MASK
                      | Gdk.EventMask.BUTTON_PRESS_MASK
                      | Gdk.EventMask.POINTER_MOTION_MASK
                      | Gdk.EventMask.SCROLL_MASK)

    def _do_expose(self, widget, context):
        cr = self.get_property('window').cairo_create()
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgb(1,1,1)
        Gdk.cairo_set_source_pixbuf(context, self.pixbuf, 0, 0)
        context.paint()

