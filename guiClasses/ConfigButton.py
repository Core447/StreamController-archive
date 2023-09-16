from gi.repository import Gtk
class ConfigButton(Gtk.Button):
    def __init__(self, label: str):
        if type(label) is not str: 
            raise TypeError("label must be a String")
        super().__init__(margin_bottom=6)
        self.buttonGrid = Gtk.Grid()
        self.buttonIcon = Gtk.Image(pixel_size=25, margin_end=10, margin_top=12.5, margin_bottom=12.5)
        self.buttonLabel = Gtk.Label(label=label)

        #Attachments
        self.set_child(self.buttonGrid)
        self.buttonGrid.attach(self.buttonIcon, 0, 0, 1, 1)
        self.buttonGrid.attach(self.buttonLabel, 1, 0, 1, 1)