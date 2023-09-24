from gi.repository import Gtk, Gdk, Adw, Gio, GLib

class StoreBatch(Gtk.Button):
    def __init__(self, label):
        super().__init__(label=label, css_classes=["official-mark-btn"], margin_end=5)
        self.connect("clicked", self.onClick)

    def onClick(self, button):
        print("OfficialMark onClick")