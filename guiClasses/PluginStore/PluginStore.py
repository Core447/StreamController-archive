from gi.repository import Gtk, Gdk, Adw, Gio, GLib
import sys, json, re, os, threading
from time import sleep
from fuzzywuzzy import fuzz, process
from urllib.parse import urlparse

# Import own modules
sys.path.append("guiClasses/PluginStore")
from PluginPreview import PluginPreview
from GitHubHelper import GitHubHelper
from InfoSaver import InfoSaver
from UpperPart import UpperPart
from StoreLoadingThread import StoreLoadingThread

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
        self.infoSaver = InfoSaver()

        self.filterOfficial = False
        self.filterVerified = False
        
        self.officials = None

        self.build()

    def onResize(self, width, height):
        print("resize")
    
    def build(self):
        # Init objects
        self.titleBar = Gtk.HeaderBar()
        self.scrolledWindow = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.scrolledWindowMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.contentBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        self.mainFlowBox = Gtk.FlowBox(vexpand=True, hexpand=True, homogeneous=True)
        self.mainFlowBox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.upperPart = UpperPart(self)
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, margin_top=10)
        print("col:", self.mainFlowBox.get_column_spacing())
        print("row:", self.mainFlowBox.get_row_spacing())

        # Attach objects
        self.set_titlebar(self.titleBar)
        self.set_child(self.mainBox)
        self.mainBox.append(self.upperPart)
        self.mainBox.append(self.scrolledWindow)
        self.scrolledWindow.set_child(self.scrolledWindowMain)
        self.scrolledWindowMain.append(self.contentBox)
        self.contentBox.append(self.mainFlowBox)
        # for i in range(0, 20):
            # self.mainFlowBox.append(PluginPreview(self))
        

        # self.loadPreviews()
        loadPreviewsThread = threading.Thread(target=self.loadPreviews)
        loadPreviewsThread.start()

        self.mainFlowBox.set_filter_func(self.filterFunc)
        self.mainFlowBox.set_sort_func(self.sortFunc)
        self.mainFlowBox.invalidate_filter()
        self.mainFlowBox.invalidate_sort()

    def filterFunc(self, child):
        searchString = self.upperPart.searchEntry.get_text()
        
        # Button filters
        if self.filterOfficial and not child.official:
            return False

        # Show everything if there is no search
        if searchString == "":
            return True
        
        ## Special filters
        # Username
        if self.normString(self.getTagValue("user", searchString)) not in [self.normString(child.userName), None]:
            return False
        # Plugin name
        if self.normString(self.getTagValue("name", searchString)) not in [self.normString(child.pluginName), None]:
            return False
        
        # Normal filters
        stringRemovedTags = self.remove_tags(searchString)
        if self.normString(stringRemovedTags) in self.normString(child.pluginName):
            return True
        if self.normString(stringRemovedTags) in self.normString(child.pluginDescription):
            return True
        if self.normString(stringRemovedTags) in self.normString(child.userName):
            return True
        
        # Allow everything which has a higher fuzzy score than 70 in the name or 40 in the description
        if fuzz.partial_ratio(self.normString(stringRemovedTags), self.normString(child.pluginName)) > 70:
            return True
        if fuzz.partial_ratio(self.normString(stringRemovedTags), self.normString(child.pluginDescription)) > 40:
            return True
        
        return False
    
    def sortFunc(self, child1, child2):
        """
        Returns:
            -1 if child1 should be before child2
            0  if child1 and child2 are equal
            1  if child2 should be before child1
        """

        searchString = self.upperPart.searchEntry.get_text()

        child1Points = 0
        child2Points = 0
        
        if self.normString(self.getTagValue("user", searchString)) == self.normString(child1.userName):
            child1Points += 1
        if self.normString(self.getTagValue("user", searchString)) == self.normString(child2.userName):
            child2Points += 1
        if self.normString(self.getTagValue("name", searchString)) == self.normString(child1.pluginName):
            child1Points += 1
        if self.normString(self.getTagValue("name", searchString)) == self.normString(child2.pluginName):
            child2Points += 1


        if child1Points == child2Points:
            stringRemovedTags = self.remove_tags(searchString)
            child1Fuzzy = fuzz.partial_ratio(child1.pluginName, stringRemovedTags)
            child2Fuzzy = fuzz.partial_ratio(child2.pluginName, stringRemovedTags)
            if child1Fuzzy > child2Fuzzy:
                child1Points += 1
            elif child1Fuzzy < child2Fuzzy:
                child2Points += 1

        if child1Points > child2Points:
            return -1
        if child1Points < child2Points:
            return 1
        return 0

    
    def normString(self, string: str) -> str:
        if string == None:
            return None
        return string.lower().replace(" ", "")

    def getTagValue(self, tag: str, string: str) -> str:
        if tag not in string:
            return
        if string.split(tag)[1][1] == '"':
            # string is a quoted string
            # return text between quotes
            quotesEnd = string.split(tag)[1][2:].find('"')
            return string.split(tag)[1][2:quotesEnd+2]
        
        # Return from tag to next space
        nextSpace = string.split(tag)[1].find(" ")
        if nextSpace == -1:
            nextSpace = len(string.split(tag)[1])
        return string.split(tag)[1][1:nextSpace]
    
    def remove_tags(self, string):
        """
        Remove all tags from a string.

        Args:
            string (str): The input string containing tags.

        Returns:
            str: The input string with all tags removed.
        """
        tag_pattern = r'\b\w+:[^\s]+\b'
        return re.sub(tag_pattern, '', string)
    
    def isOfficial(self, userName: str) -> bool:
        if self.officials == None:
            rawOfficials = self.githubHelper.getRaw("https://github.com/Core447/StreamController-Plugins", "OfficialAuthors.json", branchName="main")
            if rawOfficials == None:
                return False
            officialList = json.loads(rawOfficials)
            self.officials = officialList["officialAuthors"]
        return userName in self.officials

    def loadPreviews(self):
        while not self.app.storeLoadingThread.ready:
            print("please wait while the store is loading")
            sleep(0.5)
            continue

        for plugin in self.app.storeLoadingThread.plugins:
            pluginName = plugin["name"]
            pluginUrl = plugin["url"]
            pluginVerifiedCommit = plugin["verified-commit"]
            userName = plugin["user"]


            pluginOfficial = self.isOfficial(userName)
            # stargazers = self.githubHelper.getStargzersCount(pluginUrl)
            #TODO: To avoid exceeding the api limit the stars get loaded in the detailed view of a plugin
            stargazers = None

            manifestPath = plugin["manifestPath"]
            # Open json from path
            with open(manifestPath, "r") as f:
                manifest = json.load(f)

            pluginDescription = manifest["description"]
            thumbnailPath = plugin["thumbnailPath"]

            self.mainFlowBox.append(PluginPreview(self, pluginName, pluginDescription, thumbnailPath, userName, stargazers, pluginUrl, pluginVerifiedCommit, pluginOfficial))