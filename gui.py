from time import sleep
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk
from gi.repository import GObject, Gio
import sys
from controller import CommunicationHandler
from controller import ASSETS_PATH
from PluginBase import PluginBase
import importlib
import os
import shutil

#import guiClasses
from guiClasses.CategoryButton import CategoryButton
from guiClasses.ConfigButton import ConfigButton
from guiClasses.ActionButton import ActionButton
from guiClasses.GridButton import GridButton
from guiClasses.MultiActionConfig import MultiActionConfig
from guiClasses.PageManager import PageManager
from guiClasses.ConfigArea import ConfigArea
from guiClasses.PluginStore.PluginStore import PluginStore

#StreamDeck
from StreamDeck.DeviceManager import DeviceManager
import os

streamdecksRaw = DeviceManager().enumerate()

streamdecks = []

for deck in streamdecksRaw:
    streamdecks.append(deck.deck_type())


def createPagesList(onlyName: bool = False):
    #TODO: Delete
    pagesPath = "pages"
    pages = []
    for file in os.listdir(pagesPath):
        if file.endswith(".json"):
            if onlyName:
                pages.append(file[:-5]) # remove .json extension
                continue
            pages.append(file)
    return pages




        
        
class KeyGrid(Gtk.Grid):
    def __init__(self, app):
        super().__init__(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, column_homogeneous=True, row_homogeneous=True, hexpand=True, vexpand=True)
        self.app = app
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
                self.gridButtons.append(GridButton(self.app, self, r, c))

class DeviceSelector(Gtk.ComboBox):
    #TODO: Switch to Gtk.DropDown because combobox got deprecated in 4.10
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
        self.keyGrid.createGrid(streamdecksRaw[self.get_active()].key_layout())


allActions = {
    "Main": ["a", "b"],
    "Main1": ["a", "b"],
    "Main2": ["a", "b"],
}


class CategorySelector(Gtk.Grid):
    def __init__(self, app):
        self.app = app
        super().__init__(column_homogeneous=True)        
        self.label = Gtk.Label(label="Categories", xalign=0,
                               css_classes=["page-text"])
        self.attach(self.label, 0, 0, 1, 1)

    def loadCategories(self, categories: list):
        for row in range(len(categories)):
            categoryButton = CategoryButton(self.app, categories[row])
            self.attach(categoryButton, 0, row+1, 1, 1)
            #actionSelector = ActionSelector(self., categories[row])
            #actionSelector.loadActions(["A","B"])

class ActionSelector(Gtk.Grid):
    def __init__(self, app, categoryName):
        self.app = app
        super().__init__(column_homogeneous=True)        
        self.label = Gtk.Label(label=categoryName, xalign=0,
                               css_classes=["page-text"])
        self.attach(self.label, 0, 0, 1, 1)

    def loadActions(self, actions: list, categoryName: str):
        for row in range(len(actions)):
            actionButton = ActionButton(self.app, actions[row], "", categoryName+":"+actions[row])
            self.attach(actionButton, 0, row+1, 1, 1)
            pass


class PageSelector(Gtk.Grid):
    def __init__(self, app):
        super().__init__(margin_bottom=5, margin_top=5, margin_start=5, margin_end=5)
        self.app = app

        self.label = Gtk.Label(label="Page:", margin_end=5)      

        ## Dropdown menu
        pages = self.app.communicationHandler.createPagesList(True)
        self.dropDown = Gtk.DropDown().new_from_strings(pages)
        # self.dropDown.insert_after('a', 'm')
        self.dropDown.set_size_request(150, -1)
        # self.dropDown.set_enable_search(True) #TODO: Enable search

        self.dropDown.connect('notify::selected-item', self.onChange) # Connecting after switching to the main page to avoid double loading 

        ## Page manager
        self.pageManagerButton = Gtk.Button(icon_name='settings', tooltip_text='Page Manager')
        self.pageManagerButton.connect('clicked', self.onClickPageManager)

        # Create a grid for the dropdown menu and the settings button to link them visually
        self.settingsBox = Gtk.Box(css_classes=['linked'], orientation=Gtk.Orientation.HORIZONTAL)

        # Attachments
        self.attach(self.label, 0, 0, 1, 1)
        self.attach(self.settingsBox, 1, 0, 1, 1)
        self.settingsBox.append(self.dropDown)
        self.settingsBox.append(self.pageManagerButton)

        # PageManager object
        self.pageManager =PageManager(self.app)

        # self.settingsBox.remove(self.dropDown)
        
        # self.update()
        
    def onChange(self, dropdown, _pspec):
        selected = dropdown.props.selected_item
        if selected is not None:
            # return
            self.loadNewPageOnDeck(selected.props.string)

   
    def loadNewPageOnDeck(self, selectedPage: str):
        #TODO: change page only for selected deck
        for deckController in self.app.communicationHandler.deckController:
            deckController.loadPage(selectedPage, True)

    def onClickPageManager(self, button):
        self.pageManager.showWindow()

    def update(self):
        # Note: For now I remove the old dropdown menu and replace it with a new one because I couldn't figure out how to correctly update the menu
        
        # Get pages
        pageList = self.app.communicationHandler.createPagesList(True)
        # Remove old drop down menu
        self.settingsBox.remove(self.dropDown)

        # Create new drop down
        self.dropDown = Gtk.DropDown().new_from_strings(pageList)
        self.dropDown.set_size_request(150, -1)
        self.settingsBox.prepend(self.dropDown)
        
        ## Set active page
        # Get loaded page
        loadedPage = self.app.communicationHandler.deckController[0].loadedPage
        # Get index of loadedPage
        if loadedPage not in pageList:
            loadedPage = 'main'
        mainPageIndex = pageList.index(loadedPage)
        # Select main page
        self.dropDown.set_selected(mainPageIndex)


        

class HamburgerMenu(Gtk.MenuButton):
    def __init__(self, app):
        super().__init__()
        self.app = app

        #create a menu
        self.menu = Gio.Menu.new()
        self.menu.append("Plugin Store", "app.pluginstore")
        self.menu.append("About", "app.aboutdialog")

        #create a popover
        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(self.menu)

        #setup the menubutton
        self.set_popover(self.popover)
        self.set_icon_name("open-menu-symbolic")

class AboutDialog(Gtk.AboutDialog):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.set_transient_for(self.app.win)
        self.set_modal(self.app.win)

        self.set_authors(["Core447"])
        self.set_copyright("Copyright 2023 Core447")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_website("https://github.com/Core447/StreamController")
        self.set_website_label("GitHub")
        self.set_version("v0.1")
        self.set_program_name("StreamController")
        self.set_comments("A Linux app for the StreamDeck with plugin support")

        
        openAction = Gio.SimpleAction.new("aboutdialog", None)
        openAction.connect("activate", self.showDialog)
        self.app.add_action(openAction)
    
    def showDialog(self,action, parameter):
        self.show()







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

        self.hamburgerMenu = HamburgerMenu(self)
        self.header.pack_end(self.hamburgerMenu)

        self.aboutDialog = AboutDialog(self)


        self.pagesModel = Gtk.ListStore(str)
        for page in createPagesList(True):
            self.pagesModel.append()

        
        self.categoryScrolledWindow = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.stack.add_titled(self.categoryScrolledWindow, "Categories", "Categories")

        self.categoryGrid = CategorySelector(self)
        self.categoryScrolledWindow.set_child(self.categoryGrid)
        
     
        

        #self.categoryGrid.loadCategories(["One", "Two", "Three"])

        
        allCats = []
        for plugin in PluginBase.plugins:
            allCats.append(plugin)
        self.categoryGrid.loadCategories(allCats)    

        #self.categoryGrid.loadCategories(list(allActions.keys()))
        #self.stack.add_titled(self.categoryGrid, "categories", "Categories")


        allActions = {}
        for pluginName in list(PluginBase.plugins.keys()):
            allActions[pluginName] = []
            for action in PluginBase.plugins[pluginName].pluginActions:
                allActions[pluginName].append(action.ACTION_NAME)
        

        for key in list(allActions.keys()):
            actionScrolledWindow = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
            self.stack.add_titled(actionScrolledWindow, key, key)
            actionGrid = ActionSelector(self, key)
            actionGrid.loadActions(allActions[key], key)
            actionScrolledWindow.set_child(actionGrid)
        
        #exit()
        



        ###Create action buttons
        self.actionGrid = Gtk.Grid(column_homogeneous=True)
        #Create action buttons
        #self.createButton(self.actionGrid, 0, "Open URL")

        #Add action page to stack
        
        #add page selector                              
        self.pageSelector = PageSelector(self)




        self.stack.set_visible_child_name("Categories")

        #Drag drop
        #self.categoryGrid.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)


        #self.actionGrid.attach(self.target, 5, 5, 1, 1)


        self.leftSideGrid = builder.get_object("left-side-grid")

        
        self.keyGrid = KeyGrid(self)
        self.keyGrid.createGrid(streamdecksRaw[0].key_layout())

        #self.leftSideGrid.append(self.keyGrid)

        self.leftStack = builder.get_object("left-stack")
        self.leftStack.set_transition_type(Gtk.StackTransitionType.CROSSFADE) #nice-looking alternative: SLIDE_UP_DOWN
        #self.leftStack.append(self.keyGrid)

        self.leftMainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.leftStack.add_titled(self.leftMainBox, "main", "main")
        self.leftMainBox.append(self.pageSelector)
        self.leftMainBox.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.leftMainBox.append(self.keyGrid)


        self.keyGrid.createGrid((3, 5))

        #add multiaction edit page to stack
        self.MultiActionConfig = MultiActionConfig(self)
        self.leftStack.add_titled(self.MultiActionConfig, "multi", "multi")
    

        self.deviceSelector = DeviceSelector(self.keyGrid)
        self.header.set_title_widget(self.deviceSelector)

        self.actionBackButton = builder.get_object("action-back-button")
        self.actionBackButton.set_visible(False)
        self.actionBackButton.connect("clicked", self.goBackToCategories)


        # Add config area to the left side
        self.configArea = ConfigArea(self)
        self.leftSideGrid.append(self.configArea)

        # Link the plugin store
        self.pluginStoreAction = Gio.SimpleAction(name="pluginstore")
        self.pluginStoreAction.connect("activate", self.openPluginStore)
        self.add_action(self.pluginStoreAction)

    def openPluginStore(self, action, params):
        self.pluginStore = PluginStore(self)
        self.pluginStore.show()

    def categoryClick(self, button):
        self.stack.set_visible_child_name("actions")

    def goBackToCategories(self, button):
        self.stack.set_visible_child(self.categoryScrolledWindow)
        self.actionBackButton.set_visible(False)

    def onWindowClose(self, window):
        print("windows close")

    def quit(self, widget, _):
        print("quit")
        sys.exit()
    


#app = StreamControllerApp(application_id="com.core447.StreamController")
#app.run(sys.argv)
