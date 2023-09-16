from gi.repository import Gtk, Gdk, Adw, Gio, GLib, GdkPixbuf, Gsk, Pango
import sys

# Import own modules
sys.path.append("guiClasses/PluginStore")
from OfficialMark import OfficialMark

class PluginPreview(Gtk.FlowBoxChild):
    def __init__(self, pluginStore):
        super().__init__(width_request=100, height_request=100)
        self.build()
        
    def build(self):
        # Main button covering the hole FlowBoxChild
        self.mainButton = Gtk.Button(hexpand=True, vexpand=True, width_request=250, height_request=200,
                                     margin_start=0, margin_end=0, css_classes=["no-padding"])
        self.set_child(self.mainButton)
        # Main box covering the hole button
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, homogeneous=False)
        self.mainButton.set_child(self.mainBox)
        # Image of the plugin
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale("tmp/assets/MediaPlugin.png",
                                                         width=250, height=50, preserve_aspect_ratio=True)
        self.image = Gtk.Picture(hexpand=False,vexpand=False, css_classes=["plugin-store-image"])
        self.image.set_pixbuf(pixbuf)
        self.image.set_valign(Gtk.Align.START)
        self.image.set_size_request(2, 2)
        self.mainBox.append(self.image)
        # Bottom box with all infos
        self.bottomBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, valign=0, margin_start=5, margin_top=5)
        self.mainBox.append(self.bottomBox)
        # Label with the name of the plugin
        self.nameLabel = Gtk.Label(label="Media Plugin", halign=Gtk.Align.START, css_classes=["plugin-store-name"])
        self.bottomBox.append(self.nameLabel)
        # Marks area
        self.marksBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.START, hexpand=True, margin_top=5)
        self.bottomBox.append(self.marksBox)
        # Official mark
        self.marksBox.append(OfficialMark())
        # Description
        descriptionText = "Control your media playback from all sources"
        self.descriptionLabel = Gtk.Label(label=descriptionText, halign=Gtk.Align.START,
                                          css_classes=["plugin-store-description"], margin_top=10, wrap=True, lines=5,
                                          max_width_chars=20,
                                          ellipsize=Pango.EllipsizeMode.END,
                                          margin_bottom=10,
                                          sensitive=False
                                          )
        
        self.bottomBox.append(self.descriptionLabel)
