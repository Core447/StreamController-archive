from gi.repository import Gtk, Gdk, Adw, Gio, GLib
import sys, json
from urllib.parse import urlparse

# Import own modules
sys.path.append("guiClasses/PluginStore")
from PluginPreview import PluginPreview
from GitHubHelper import GitHubHelper

class PluginStore(Gtk.ApplicationWindow):
    """
    In the plugin store the user can install plugins.
    """
    def __init__(self, app):
        self.app = app
        super().__init__(title="Plugin Store",
                         default_height=750,
                         default_width=1050,
                         transient_for=self.app.win,
                         modal=True
                         )
        self.githubHelper = GitHubHelper()
        self.build()

    def onResize(self, width, height):
        print("resize")
    
    def build(self):
        # Init objects
        self.titleBar = Gtk.HeaderBar()
        self.scrolledWindow = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.topBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        self.topBox.append(Gtk.Label(label="Plugins"))
        self.contentBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        self.mainFlowBox = Gtk.FlowBox(vexpand=True, hexpand=True, homogeneous=True)
        self.mainFlowBox.set_selection_mode(Gtk.SelectionMode.NONE)
        print("col:", self.mainFlowBox.get_column_spacing())
        print("row:", self.mainFlowBox.get_row_spacing())

        # Attach objects
        self.set_titlebar(self.titleBar)
        self.set_child(self.scrolledWindow)
        self.scrolledWindow.set_child(self.mainBox)
        self.mainBox.append(self.topBox)
        self.mainBox.append(self.contentBox)
        self.contentBox.append(self.mainFlowBox)
        # for i in range(0, 20):
            # self.mainFlowBox.append(PluginPreview(self))

        self.loadPreviews()

    def loadPreviews(self):
        pluginList = self.githubHelper.getRaw("https://github.com/Core447/StreamController-Plugins", "Plugins.json", branchName="main")
        print(pluginList)
        pluginList = json.loads(pluginList)

        for plugin in pluginList:
            # Get backend infos
            pluginUrl = pluginList[plugin]["url"]
            pluginVerifiedCommit = pluginList[plugin]["verified-commit"]
            

            # Get frontend infos
            pluginManifest = json.loads(self.githubHelper.getRaw(pluginUrl, "manifest.json", branchName="main"))
            pluginName = pluginManifest["name"]
            pluginDescription = pluginManifest["description"]

            # Save thumbnail
            thumbnailPath = self.githubHelper.downloadThumbnail(pluginUrl, pluginManifest["thumbnail"], commitSHA=pluginVerifiedCommit)

            # Get user infos
            userName = self.githubHelper.getUserNameFromUrl(pluginUrl)
            stargazers = self.githubHelper.getStargzersCount(pluginUrl)

            # Load the preview in the store
            self.mainFlowBox.append(PluginPreview(self, pluginName, pluginDescription, thumbnailPath, userName, stargazers, pluginUrl))
