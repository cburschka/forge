from gi.repository import Gtk

class AboutDialog(Gtk.Dialog):
    def __init__(self, window):
        Gtk.Dialog.__init__(self, 'Forge 0.0.0', window, Gtk.DialogFlags.MODAL,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        label = Gtk.Label("Forge is a product of the Ermarian Network, 2013.")
        link = Gtk.LinkButton("http://github.com/cburschka/forge-python", "http://github.com/cburschka/forge-python")
        content_area = self.get_content_area()
        content_area.add(label)
        content_area.add(link)

    def run(self):
        Gtk.Dialog.show_all(self)
        Gtk.Dialog.run(self)
        Gtk.Dialog.destroy(self)

class OpenScenarioDialog(Gtk.FileChooserDialog):
    def __init__(self, window):
        Gtk.FileChooserDialog.__init__(self, 'Open Scenario File', window, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        bas_filter = Gtk.FileFilter()
        bas_filter.set_name("BoA Scenario Files - *.bas")
        bas_filter.add_pattern("*.bas")
        self.add_filter(bas_filter)

        
    def run(self):
        response = Gtk.FileChooserDialog.run(self)
        if response == Gtk.ResponseType.OK:
            open_file = self.get_filename()
        else:
            open_file = None
        self.destroy()
        return open_file
