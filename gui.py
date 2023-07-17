from time import sleep
from gi.repository import Gtk, Adw, Gdk
from gi.repository import GObject, Gio
import sys
import gi
from controller import CommunicationHandler
from controller import ASSETS_PATH
from PluginBase import PluginBase
import importlib
import os
import shutil
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

#import guiClasses
from guiClasses.CategoryButton import CategoryButton
from guiClasses.ConfigButton import ConfigButton
from guiClasses.ActionButton import ActionButton
from guiClasses.GridButton import GridButton
from guiClasses.MultiActionConfig import MultiActionConfig


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
            #actionSelector = ActionSelector(self., categories[row])
            #actionSelector.loadActions(["A","B"])

class ActionSelector(Gtk.Grid):
    def __init__(self, stack, categoryName):
        self.stack = stack
        super().__init__(column_homogeneous=True)        
        self.label = Gtk.Label(label=categoryName, xalign=0,
                               css_classes=["page-text"])
        self.attach(self.label, 0, 0, 1, 1)

        self.stack.add_titled(self, categoryName, categoryName)

    def loadActions(self, actions: list, categoryName: str):
        for row in range(len(actions)):
            actionButton = ActionButton(self, row+1, actions[row], "", categoryName+":"+actions[row])
            pass


class PageSelector(Gtk.Grid):
    def __init__(self, app):
        super().__init__(margin_bottom=5, margin_top=5, margin_start=5, margin_end=5)
        self.app = app

        self.label = Gtk.Label(label="Page:", margin_end=5)

        #ComboBox
        self.pagesModel = Gtk.ListStore(str)
        for page in self.createPagesList(True):
            self.pagesModel.append([page])
        
        self.comboBox = Gtk.ComboBox.new_with_model_and_entry(self.pagesModel)
        #self.comboBox = Gtk.ComboBoxText.new_with_model_and_entry(self.pagesModel)
        self.comboBox.set_entry_text_column(0)
        self.comboBox.set_can_focus(True)
        self.comboBox.set_hexpand(False)
        
        self.comboBox.connect("changed", self.onChange)
        #self.comboBox.connect("leave-notify-event", self.onEntryFocusOut)
        self.focusCtrl = Gtk.EventControllerFocus().new()
        self.focusCtrl.connect("leave", self.onEntryFocusOut)
        self.comboBox.add_controller(self.focusCtrl)
        #TODO: Also add event for return key

        #Attachments
        self.attach(self.label, 0, 0, 1, 1)
        self.attach(self.comboBox, 1, 0, 1, 1)


        #set first page to default
        for page in range(len(self.pagesModel)):
            print(self.pagesModel[page][0])
            if self.pagesModel[page][0] == "main":
                print(page)
                break #FIXME: setting the default page causes the programm to freeze
                self.comboBox.set_active(page)
        

    def createPagesList(self, onlyName: bool = False):
        pagesPath = "pages"
        pages = []
        for file in os.listdir(pagesPath):
            if file.endswith(".json"):
                if onlyName:
                    pages.append(file[:-5]) # remove .json extension
                    continue
                pages.append(file)
        return pages

        

    def onChange(self, combo: Gtk.ComboBox):
        print(combo.get_child().get_text())
        self.handlePageSelectorConfirmation()
    
    def onEntryFocusOut(self, event):
        self.handlePageSelectorConfirmation()
        

    
    def handlePageSelectorConfirmation(self):
        print(self.comboBox.get_child().get_text())
        if self.comboBox.get_child().get_text() in self.createPagesList(True):
            #page already exists
            #TODO: change page only for selected deck
            for deckController in self.app.communicationHandler.deckController:
                deckController.loadPage(self.comboBox.get_child().get_text())
        else:
            #page does not exist yet, we need to create it
            #TODO: Show a dialog to the user to accept the creation of a new page
            self.pagesModel.append([self.comboBox.get_child().get_text()])
            if(os.path.exists(os.path.join("pages", self.comboBox.get_child().get_text()+".json"))):
                return
            shutil.copy(os.path.join(ASSETS_PATH, "templates", "emptyPage.json"), os.path.join("pages", self.comboBox.get_child().get_text()+".json"))


            #TODO: change page only for selected deck
            for deckController in self.app.communicationHandler.deckController:
                deckController.loadPage(self.comboBox.get_child().get_text())
    
class HamburgerMenu(Gtk.MenuButton):
    def __init__(self, app):
        super().__init__()
        self.app = app

        #create a menu
        self.menu = Gio.Menu.new()
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
            actionGrid.loadActions(allActions[key], key)

        
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
        #print(streamdecksRaw[0].key_layout())

        #self.leftSideGrid.append(self.keyGrid)

        self.leftStack = builder.get_object("left-stack")
        self.leftStack.set_transition_type(Gtk.StackTransitionType.CROSSFADE) #nice-looking alternative: SLIDE_UP_DOWN
        #self.leftStack.append(self.keyGrid)

        self.leftMainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.leftStack.add_titled(self.leftMainBox, "grid", "grid")
        self.leftMainBox.append(self.pageSelector)
        self.leftMainBox.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.leftMainBox.append(self.keyGrid)


        self.keyGrid.createGrid((3, 5))


        #add grid where all action configs can be displayed
        self.actionConfigBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, margin_bottom=10)
        self.leftSideGrid.append(self.actionConfigBox)


        #add multiaction edit page to stack
        self.MultiActionConfig = MultiActionConfig(self)
        self.leftStack.add_titled(self.MultiActionConfig, "multi", "multi")
    

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
