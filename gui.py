from time import sleep
from gi.repository import Gtk, Adw, Gdk
from gi.repository import GObject, Gio
import sys
import gi
from controller import CommunicationHandler
from PluginBase import PluginBase
import importlib
import os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

#import guiClasses
from guiClasses.CategoryButton import CategoryButton
from guiClasses.ConfigButton import ConfigButton
from guiClasses.ActionButton import ActionButton
from guiClasses.GridButton import GridButton


#StreamDeck
from StreamDeck.DeviceManager import DeviceManager
import os

streamdecksRaw = DeviceManager().enumerate()

streamdecks = []

for deck in streamdecksRaw:
    streamdecks.append(deck.deck_type())


def createPagesList():
    pagesPath = "pages"
    
    pages = []
    for file in os.listdir(pagesPath):
        if file.endswith(".json"):
            pages.append(file)
    return pages

print(createPagesList())


        
        
class KeyGrid(Gtk.Grid):
    def __init__(self):
        super().__init__(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, column_homogeneous=True, row_homogeneous=True, hexpand=True, vexpand=True)
        self.loadedRows = 0
        self.loadedColumns = 0
        self.gridButtons = []

    
    def createGrid(self, layout: tuple):
        self.gridButtons = []
        if type(layout) is not tuple:
            raise TypeError("layout needs to be a tuple")
        if len(layout) != 2:
            raise IndexError("layout needs to be a 1x2 tuple")
        
        
        if self.loadedRows == layout[0] and self.loadedColumns == layout[1]:
            return
        
        while(self.get_first_child() != None):
            self.remove(self.get_first_child())

        for r in range(layout[0]):
            for c in range(layout[1]):
                self.gridButtons.append(GridButton(self, r, c))

class DeviceSelector(Gtk.ComboBox):
    def __init__(self, keyGrid: KeyGrid):
        self.keyGrid = keyGrid

        self.createDeviceList()
        super().__init__(model=self.deviceList, has_entry=True)      
        
        self.set_entry_text_column(0)
        self.set_can_focus(False)
        self.connect("changed", self.onChange)


    def createDeviceList(self):
        self.deviceList = Gtk.ListStore(str)
        for deck in streamdecksRaw:
            self.deviceList.append([deck.deck_type()])

    def onChange(self, combo):
        print(self.get_active())
        print(streamdecksRaw[0].deck_type())
        self.keyGrid.createGrid(streamdecksRaw[self.get_active()].key_layout())


allActions = {
    "Main": ["a", "b"],
    "Main1": ["a", "b"],
    "Main2": ["a", "b"],
}


class CategorySelector(Gtk.Grid):
    def __init__(self, app, stack):
        self.stack = stack
        self.app = app
        super().__init__(column_homogeneous=True)        
        self.label = Gtk.Label(label="Categories", xalign=0,
                               css_classes=["page-text"])
        self.attach(self.label, 0, 0, 1, 1)
        self.stack.add_titled(self, "Categories", "Categories")

    def loadCategories(self, categories: list):
        print("*****************")
        
        for row in range(len(categories)):
            categoryButton = CategoryButton(self.app, self, self.stack, row+1, categories[row])
            #actionSelector = ActionSelector(self.stack, categories[row])
            #actionSelector.loadActions(["A","B"])

class ActionSelector(Gtk.Grid):
    def __init__(self, stack, categoryName):
        self.stack = stack
        super().__init__(column_homogeneous=True)        
        self.label = Gtk.Label(label=categoryName, xalign=0,
                               css_classes=["page-text"])
        self.attach(self.label, 0, 0, 1, 1)

        self.stack.add_titled(self, categoryName, categoryName)

    def loadActions(self, actions: list):
        for row in range(len(actions)):
            actionButton = ActionButton(self, row+1, actions[row], "")
            pass



class StreamControllerApp(Adw.Application):
    def __init__(self, communicationHandler: CommunicationHandler, **kwargs):
        super().__init__(**kwargs)
        self.communicationHandler = communicationHandler
        self.connect('activate', self.on_activate)
        #self.connect('destroy', self.onWindowClose)
        #self.create_action('quit', self.quit)

        

    def on_activate(self, app):
        # Create a Builder
        builder = Gtk.Builder()
        builder.add_from_file("streamcontroller.ui")

        # Obtain and show the main window
        self.win = builder.get_object("main_window")
        # Application will close once it no longer has active windows attached to it
        self.win.set_application(self)
        self.win.present()

        self.model = builder.get_object("model")
        self.buttonGrid = builder.get_object("buttonGrid")
        

        renderer = Gtk.CellRendererPixbuf()
        # load css
        screen = Gdk.Display.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_path("style.css")
        Gtk.StyleContext.add_provider_for_display(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.stack = builder.get_object("stack")

        self.header = builder.get_object("header")

        self.name_store = Gtk.ListStore(str)


        self.pagesModel = Gtk.ListStore(str)
        for page in createPagesList():
            self.pagesModel.append([page.replace(".json","")])

        
        
        
        self.g = builder.get_object("page-selector-grid")
        
        self.pageSelector = Gtk.ComboBox.new_with_model_and_entry(self.pagesModel)
        self.pageSelector.set_entry_text_column(0)
        self.pageSelector.set_can_focus(True)
        self.pageSelector.set_hexpand(False)

        self.g.attach(self.pageSelector, 1, 0, 1, 1)
        

        self.categoryGrid = CategorySelector(self, self.stack)
        #self.categoryGrid.loadCategories(["One", "Two", "Three"])

        
        allCats = []
        for plugin in PluginBase.plugins:
            print(plugin)
            allCats.append(plugin)
        self.categoryGrid.loadCategories(allCats)    

        #self.categoryGrid.loadCategories(list(allActions.keys()))
        #self.stack.add_titled(self.categoryGrid, "categories", "Categories")


        allActions = {}
        print("loading...")
        print(PluginBase.plugins)
        for pluginName in list(PluginBase.plugins.keys()):
            print(pluginName)
            allActions[pluginName] = []
            for action in PluginBase.plugins[pluginName].pluginActions:
                print(action.ACTION_NAME)
                allActions[pluginName].append(action.ACTION_NAME)
        
        print(allActions)


        for key in list(allActions.keys()):
            actionGrid = ActionSelector(self.stack, key)
            actionGrid.loadActions(allActions[key])

        
        #exit()
        



        ###Create action buttons
        self.actionGrid = Gtk.Grid(column_homogeneous=True)
        #Create action buttons
        #self.createButton(self.actionGrid, 0, "Open URL")

        #Add action page to stack
        self.stack.add_titled(self.actionGrid, "Media", "Media")




        self.stack.set_visible_child_name("categories")

        #Drag drop
        #self.categoryGrid.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)


        #self.actionGrid.attach(self.target, 5, 5, 1, 1)


        self.leftSideGrid = builder.get_object("bbox")
        
        self.keyGrid = KeyGrid()
        self.keyGrid.createGrid(streamdecksRaw[0].key_layout())
        #print(streamdecksRaw[0].key_layout())

        self.leftSideGrid.append(self.keyGrid)

        self.keyGrid.createGrid(self.deck.key_layout())


        self.deviceSelector = DeviceSelector(self.keyGrid)
        self.header.pack_start(self.deviceSelector)

        self.actionBackButton = builder.get_object("action-back-button")
        self.actionBackButton.set_visible(False)
        self.actionBackButton.connect("clicked", self.goBackToCategories)


        


    def categoryClick(self, button):
        print("catClick")
        self.stack.set_visible_child_name("actions")

    def goBackToCategories(self, button):
        self.stack.set_visible_child(self.categoryGrid)
        self.actionBackButton.set_visible(False)

    def onWindowClose(self, window):
        print("windows close")

    def quit(self, widget, _):
        print("quit")
        sys.exit()
    


#app = StreamControllerApp(application_id="com.core447.StreamController")
#app.run(sys.argv)
