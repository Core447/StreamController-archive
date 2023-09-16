from gi.repository import Gtk, Gdk, Adw, Gio, GLib

class OfficialMark(Gtk.Button):
    def __init__(self):
        super().__init__(label="official", css_classes=["official-mark-btn"])
        self.connect("clicked", self.onClick)

    def onClick(self, button):
        print("OfficialMark onClick")