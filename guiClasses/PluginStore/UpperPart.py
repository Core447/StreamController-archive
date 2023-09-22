from gi.repository import Gtk, Gdk, Adw, Gio, GLib

class UpperPart(Gtk.Box):
    def __init__(self, pluginStore):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=True, margin_start=10, margin_end=10, margin_top=1)
        self.pluginStore = pluginStore
        self.build()

    def build(self):
        self.searchEntry = Gtk.SearchEntry(hexpand=True,
                                           placeholder_text="Search for plugins")
        self.searchEntry.connect("search-changed", self.onSearchChange)
        self.append(self.searchEntry)

        self.filterBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, margin_top=5)
        self.append(self.filterBox)

        self.filterLabel = Gtk.Label(label="Filter:")
        self.filterBox.append(self.filterLabel)

        # Build filter buttons
        self.officialButton = OfficialButton(self, margin_start=5)
        self.verifiedButton = VerifiedButton(self, margin_start=5)
        self.filterBox.append(self.officialButton)
        self.filterBox.append(self.verifiedButton)
        # Separator
        self.separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin_top=10, hexpand=True)
        self.append(self.separator)

    def onSearchChange(self, widget):
        print("Search entry changed")
        self.pluginStore.mainFlowBox.invalidate_filter()
        self.pluginStore.mainFlowBox.invalidate_sort()

class OfficialButton(Gtk.Button):
    def __init__(self, upperPart, **kwargs):
        self.upperPart = upperPart
        super().__init__(label="Official", css_classes=["filter-button-unselected"], **kwargs)
        self.connect("clicked", self.onClick)

    def onClick(self, widget):
        if "filter-button-unselected" in self.get_css_classes():
            self.upperPart.pluginStore.filterOfficial = True
            self.set_css_classes(["filter-button-selected"])
        else:
            self.upperPart.pluginStore.filterOfficial = False
            self.set_css_classes(["filter-button-unselected"])
        self.upperPart.pluginStore.mainFlowBox.invalidate_filter()
        self.upperPart.pluginStore.mainFlowBox.invalidate_sort()

class VerifiedButton(Gtk.Button):
    def __init__(self, upperPart, **kwargs):
        self.upperPart = upperPart
        super().__init__(label="Verified", css_classes=["filter-button-unselected"], **kwargs)
        self.connect("clicked", self.onClick)

    def onClick(self, widget):
        if "filter-button-unselected" in self.get_css_classes():
            self.upperPart.pluginStore.filterVerified = True
            self.set_css_classes(["filter-button-selected"])
        else:
            self.upperPart.pluginStore.filterVerified = False
            self.set_css_classes(["filter-button-unselected"])
        self.upperPart.pluginStore.mainFlowBox.invalidate_filter()
        self.upperPart.pluginStore.mainFlowBox.invalidate_sort()