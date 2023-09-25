import gi
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import WebKit

from gi.repository import Gtk, Gdk, Gio, Pango, GdkPixbuf
import sys

# Import own modules
sys.path.append("guiClasses/PluginStore")
from StoreBatch import StoreBatch

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

    def load(self, pluginName, userName, thumbnailPath, description, markUp, pluginUrl, official = False, verified = False):
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
        if official or verified:
            self.batchesBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, margin_top=10)
            self.bottomBox.append(self.batchesBox)
            if official:
                self.batchesBox.append(StoreBatch("official"))
            if verified:
                self.batchesBox.append(StoreBatch("verified"))

        # User name
        self.userNameLabel = Gtk.Label(label=f"By {userName}", xalign=0, sensitive=False, margin_top=7, css_classes=["bold"])
        self.bottomBox.append(self.userNameLabel)

        # Short description
        self.shortDescriptionLabel = Gtk.Label(label=description, css_classes=["plugin-store-detailed-view-description"], xalign=0, margin_top=10)
        self.bottomBox.append(self.shortDescriptionLabel)

        # Markup text
        # self.markupLabel = Gtk.Label(css_classes=["store-detailed-markup"], xalign=0, margin_top=25, wrap=True, use_markup=True)
        # self.markupLabel.set_markup(markUp)
        # self.bottomBox.append(self.markupLabel)

        # Github label
        self.githubLabel = Gtk.Label(css_classes=["store-detailed-github-label"], xalign=0, margin_top=25, label="GitHub:")
        self.bottomBox.append(self.githubLabel)

        # WebKit
        self.webView = WebKit.WebView(hexpand=True, vexpand=True, height_request=700, margin_end=7)
        self.webView.load_uri(pluginUrl)
        self.bottomBox.append(self.webView)

        threading.Thread(target=self.hideDivs).start()

    def hideDivs(self):
        while self.webView.is_loading():
            continue

        self.webHideByClassName("AppHeader")
        self.webHideByClassName("Header-old") # The old header is used when accessing github with webkit
        # self.webHideByClassName("BorderGrid-cell")

    def webHideByClassName(self, className):
        js_code = f"var elementsToHide = document.getElementsByClassName('{className}'); if (elementsToHide.length > 0) for (var i = 0; i < elementsToHide.length; i++) elementsToHide[i].style.display = 'none';"
        self.webView.evaluate_javascript(js_code, -1, None, None, None, None, None)

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