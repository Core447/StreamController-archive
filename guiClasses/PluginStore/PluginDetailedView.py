from gi.repository import Gtk, Gdk, Gio, Pango, GdkPixbuf
import sys

# Import own modules
sys.path.append("guiClasses/PluginStore")
from OfficialMark import OfficialMark

class PluginDetailedView(Gtk.ScrolledWindow):
    def __init__(self, pluginStore):
        self.pluginStore = pluginStore
        super().__init__(vexpand=True, hexpand=True)

        self.build()

    def build(self):
        self.backButton = Gtk.Button(icon_name="go-previous-symbolic")
        self.pluginStore.titleBar.pack_start(self.backButton)
        self.backButton.connect("clicked", self.onBack)
        self.backButton.hide()
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.set_child(self.mainBox)

    def load(self, pluginName, userName, thumbnailPath, description, markUp, official = False):
        self.clear()

        self.imageBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            thumbnailPath,
            width=1000,
            height=360,
            preserve_aspect_ratio=False
        )
        # self.paintable = Gdk.Paintable(pixbuf=self.pixbuf)
        self.image = Gtk.Picture(
            hexpand=False,
            vexpand=True,
            content_fit=Gtk.ContentFit.COVER,
            height_request=90,
            # paintable=self.paintable
        )
        self.mainBox.append(self.imageBox)
        self.image.set_pixbuf(self.pixbuf)
        self.imageBox.append(self.image)
        self.bottomBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, height_request=600, css_classes=["bottom-box"])
        self.mainBox.append(self.bottomBox)

        ## Text
        self.pluginLabel = Gtk.Label(label=pluginName, css_classes=["store-detailed-plugin-name"], xalign=0, margin_top=20)
        self.bottomBox.append(self.pluginLabel)

        # Batches
        if official:
            self.batchesBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, margin_top=10)
            self.bottomBox.append(self.batchesBox)
            self.batchesBox.append(OfficialMark())

        # User name
        self.userNameLabel = Gtk.Label(label=f"By {userName}", xalign=0, sensitive=False, margin_top=7, css_classes=["bold"])
        self.bottomBox.append(self.userNameLabel)

        # Short description
        self.shortDescriptionLabel = Gtk.Label(label=description, css_classes=["plugin-store-detailed-view-description"], xalign=0, margin_top=10)
        self.bottomBox.append(self.shortDescriptionLabel)

        # Markup text
        self.markupLabel = Gtk.Label(label=markUp, css_classes=["store-detailed-markup"], xalign=0, margin_top=25, wrap=True)
        self.markupLabel.set_markup(markUp)
        self.bottomBox.append(self.markupLabel)

    def showLast(self):
        if self.mainBox.get_first_child() is None:
            # No last plugin
            return
        self.pluginStore.mainStack.set_visible_child_name("PluginDetailedView")
        self.backButton.show()

    def clear(self):
        while self.mainBox.get_first_child() is not None:
            self.mainBox.remove(self.mainBox.get_first_child())

    def show(self):
        self.pluginStore.mainStack.set_visible_child_name("PluginDetailedView")

        # Add back button to title bar
        self.backButton.show()

    def hide(self):
        self.pluginStore.mainStack.set_visible_child_name("overview")
        self.backButton.hide()

    def onBack(self, button):
        self.hide()