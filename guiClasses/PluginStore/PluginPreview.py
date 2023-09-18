from gi.repository import Gtk, Gdk, Adw, Gio, GLib, GdkPixbuf, Gsk, Pango
import sys

# Import own modules
sys.path.append("guiClasses/PluginStore")
from OfficialMark import OfficialMark

class PluginPreview(Gtk.FlowBoxChild):
    def __init__(self, pluginStore, pluginName, pluginDescription, thumbnailPath, userName, stargazers):
        self.pluginStore = pluginStore
        self.pluginName = pluginName
        self.pluginDescription = pluginDescription
        self.thumbnailPath = thumbnailPath
        self.userName = userName
        self.stargazers = stargazers

        super().__init__(width_request=100, height_request=100)
        self.build()
        
    def build(self):
        self.mainBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=False,
            css_classes=["no-bottom-rounding"]
        )
        self.set_child(self.mainBox)

        self.mainButton = Gtk.Button(
            hexpand=True,
            vexpand=False,
            width_request=250,
            height_request=200,
            margin_start=0,
            margin_end=0,
            css_classes=["no-padding", "no-bottom-rounding"]
        )
        self.mainBox.append(self.mainButton)

        self.mainButtonBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=False,
            homogeneous=False
        )
        self.mainButton.set_child(self.mainButtonBox)

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            self.thumbnailPath,
            width=250,
            height=90,
            preserve_aspect_ratio=False
        )
        self.image = Gtk.Picture(
            hexpand=False,
            css_classes=["plugin-store-image"],
            content_fit=Gtk.ContentFit.COVER,
            height_request=90,
            width_request=250,
            vexpand_set=True
        )
        self.image.set_pixbuf(self.pixbuf)
        self.image.set_valign(Gtk.Align.START)
        self.mainButtonBox.append(self.image)

        self.bottomBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=False,
            valign=0,
            margin_start=5,
            margin_top=5
        )
        self.mainButtonBox.append(self.bottomBox)

        self.nameLabel = Gtk.Label(
            label=self.pluginName,
            halign=Gtk.Align.START,
            css_classes=["plugin-store-name"]
        )
        self.bottomBox.append(self.nameLabel)

        self.marksBox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.START,
            hexpand=True,
            margin_top=5
        )
        self.bottomBox.append(self.marksBox)

        self.marksBox.append(OfficialMark())

        self.userNameLabel = Gtk.Label(
            label=f"By {self.userName}",
            halign=Gtk.Align.START,
            sensitive=False,
            margin_start=2,
            margin_top=7
        )
        self.bottomBox.append(self.userNameLabel)

        self.stargazersLabel = Gtk.Label(
            label=f"{self.stargazers} GitHub Stars",
            halign=Gtk.Align.START,
            sensitive=False,
            margin_start=2,
            margin_top=2
        )
        self.bottomBox.append(self.stargazersLabel)

        self.descriptionLabel = Gtk.Label(
            label=self.pluginDescription,
            halign=Gtk.Align.START,
            css_classes=["plugin-store-description"],
            margin_top=7,
            wrap=True,
            lines=5,
            max_width_chars=20,
            ellipsize=Pango.EllipsizeMode.END,
            margin_bottom=10
        )
        self.bottomBox.append(self.descriptionLabel)

        self.buttonBox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.START,
            hexpand=True,
            margin_top=0,
            css_classes=["gray"]
        )

        self.downloadButton = Gtk.Button(
            icon_name="download-symbolic",
            width_request=50,
            vexpand=False,
            css_classes=["no-top-rounding"]
        )
        self.mainBox.append(self.downloadButton)
        self.downloadButton.connect("clicked", self.onClickDownload)

    def onClickDownload(self, widget):
        print("download")