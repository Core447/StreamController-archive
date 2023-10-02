from gi.repository import Gtk, Gdk, Adw, Gio, GLib
from time import sleep
import threading

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

        # Update button
        self.updateButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, margin_top=5)
        self.append(self.updateButtonBox)

        self.updateButton = UpdateButton(self)
        self.updateButtonBox.append(self.updateButton)

        # Separator
        self.separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin_top=10, hexpand=True)
        self.append(self.separator)

    def onSearchChange(self, widget):
        print("Search entry changed")
        self.pluginStore.mainFlowBox.invalidate_filter()
        self.pluginStore.mainFlowBox.invalidate_sort()

class UpdateButton(Gtk.Button):
    def __init__(self, upperPart):
        self.upperPart = upperPart
        super().__init__(label="Search for updates", css_classes=["update-button-search"])
        self.connect("clicked", self.onClick)

        updatesAvailable = False

        self.build()

    def build(self):
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.set_child(self.mainBox)

        self.icon = Gtk.Image(icon_name="system-search")
        self.mainBox.append(self.icon)

        self.label = Gtk.Label(label="Search for updates", margin_start=3)
        self.mainBox.append(self.label)

    def onClick(self, widget):
        print("Update button clicked")
        if self.label.get_text() == "Search for updates":
            self.label.set_label("Searching for updates")
            self.set_sensitive(False)
            threading.Thread(target=self.checkForUpdates).start()
        elif self.label.get_text() == "Install updates":
            self.label.set_label("Installing updates")
            self.set_sensitive(False)
            threading.Thread(target=self.installUpdates).start()

    def installUpdates(self):
        self.upperPart.pluginStore.app.storeLoadingThread.installUpdates()
        self.updatesAvailable = False
        self.updateStatus()
        
    def checkForUpdates(self) -> bool:
        self.updatesAvailable = self.upperPart.pluginStore.app.storeLoadingThread.checkForUpdates()

        self.updateStatus()

    def updateStatus(self):
        if self.updatesAvailable:
            self.label.set_label("Install updates")
            self.set_sensitive(True)
            self.set_css_classes(["update-button-search-available"])
        else:
            self.label.set_label("You're up to date")
            self.set_css_classes(["update-button-search-uptodate"])

            threading.Thread(target=self.resetToNormalState).start()

    def resetToNormalState(self):
        sleep(3)
        self.set_sensitive(True)
        self.set_css_classes(["update-button-search"])
        self.label.set_label("Search for updates")


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