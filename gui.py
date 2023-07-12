from time import sleep
from gi.repository import Gtk, Adw, Gdk
from gi.repository import GObject, Gio
import sys
import gi
from controller import CommunicationHandler
from PluginBase import PluginBase
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


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


class ConfigButton(Gtk.Button):
    def __init__(self, label: str):
        if type(label) is not str: 
            raise TypeError("label must be a String")
        super().__init__(margin_bottom=6)
        self.buttonGrid = Gtk.Grid()
        self.buttonIcon = Gtk.Image(pixel_size=25, margin_end=10, margin_top=12.5, margin_bottom=12.5)
        self.buttonLabel = Gtk.Label(label=label)

        #Attachments
        self.set_child(self.buttonGrid)
        self.buttonGrid.attach(self.buttonIcon, 0, 0, 1, 1)
        self.buttonGrid.attach(self.buttonLabel, 1, 0, 1, 1)






class CategoryButton(ConfigButton):
    def __init__(self, grid, stack: Gtk.Stack, row, label):
        self.label = label
        self.stack = stack
        super().__init__(label)
        self.buttonIcon.set_from_icon_name("stock_open")

        grid.attach(self, 0, row, 1, 1)
        self.connect("clicked", self.onClick)

    def onClick(self, button):
        self.stack.set_visible_child_name(self.label)
        

class ActionButton(ConfigButton):
    def __init__(self, grid, row, label, iconPath):
        super().__init__(label)
        self.buttonIcon.set_from_file(iconPath)

        self.createDnD()
        grid.attach(self, 0, row, 1, 1)

    def createDnD(self):
        #Create all elements needed for drag and drop      
        dnd = Gtk.DragSource()
        dnd.set_actions(Gdk.DragAction.COPY)
        dnd.connect('prepare', self.on_dnd_prepare)
        dnd.connect('drag-begin', self.on_dnd_begin)
        dnd.connect('drag-end', self.on_dnd_end)
        self.buttonGrid.add_controller(dnd)

    def on_dnd_prepare(self, drag_source, x, y):
        print(f'in on_dnd_prepare(); drag_source={drag_source}, x={x}, y={y}')
       
        drag_source.set_icon(
            Gtk.WidgetPaintable.new(self),
            self.get_width() / 2, self.get_height() / 2
        )

        content = Gdk.ContentProvider.new_for_value(self)
        return content

    def on_dnd_begin(self, drag_source, data):
        content = data.get_content()
        print(f'in on_dnd_begin(); drag_source={drag_source}, data={data}, content={content}')

    def on_dnd_end(self, drag, drag_data, flag):
        print(f'in on_dnd_end(); drag={drag}, drag_data={drag_data}, flag={flag}')


class GridButton(Gtk.Button):
    def __init__(self, grid: Gtk.Grid, row: int, column: int):
        super().__init__()
        self.set_css_classes(["gridButton"])

        grid.attach(self, column, row, 1, 1) 

        #Drag and drop
        #button.connect('drag_begin', self.dragBegin )

        #button.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        #button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)

        
        dnd = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        dnd.connect('drop', self.on_dnd_drop)
        dnd.connect('accept', self.on_dnd_accept)
        dnd.connect('enter', self.on_dnd_enter)
        dnd.connect('motion', self.on_dnd_motion)
        dnd.connect('leave', self.on_dnd_leave)
        self.add_controller(dnd)      
    
    def on_dnd_drop(self, drop_target, value, x, y):
        print(f'in on_dnd_drop(); value={value}, x={x}, y={y}')
        print(list(value))

    def on_dnd_accept(self, drop, user_data):
        print(f'in on_dnd_accept(); drop={drop}, user_data={user_data}')
        return True

    def on_dnd_enter(self, drop_target, x, y):
        print(f'in on_dnd_enter(); drop_target={drop_target}, x={x}, y={y}')
        return Gdk.DragAction.COPY

    def on_dnd_motion(self, drop_target, x, y):
        print(f'in on_dnd_motion(); drop_target={drop_target}, x={x}, y={y}')
        return Gdk.DragAction.COPY

    def on_dnd_leave(self, user_data):
        print(f'in on_dnd_leave(); user_data={user_data}')
        
        
class KeyGrid(Gtk.Grid):
    def __init__(self):
        super().__init__(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        self.loadedRows = 0
        self.loadedColumns = 0

    
    def createGrid(self, layout: tuple):
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
                GridButton(self, r, c)

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
    def __init__(self, stack):
        self.stack = stack
        super().__init__(column_homogeneous=True)        
        self.label = Gtk.Label(label="Categories", xalign=0,
                               css_classes=["page-text"])
        self.attach(self.label, 0, 0, 1, 1)
        self.stack.add_titled(self, "Categories", "Categories")

    def loadCategories(self, categories: list):
        print("*****************")
        
        for row in range(len(categories)):
            categoryButton = CategoryButton(self, self.stack, row+1, categories[row])
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
        

        self.categoryGrid = CategorySelector(self.stack)
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


        self.leftSideGrid = builder.get_object("left-side-grid")
        
        self.keyGrid = KeyGrid()
        self.keyGrid.createGrid(streamdecksRaw[0].key_layout())
        #print(streamdecksRaw[0].key_layout())

        self.leftSideGrid.attach(self.keyGrid, 0, 1, 1, 1)

        self.keyGrid.createGrid((4, 8))


        self.deviceSelector = DeviceSelector(self.keyGrid)
        self.header.pack_start(self.deviceSelector)


        


    def categoryClick(self, button):
        print("catClick")
        self.stack.set_visible_child_name("actions")

    def goBack(self, button):
        print("catClick")
        self.stack.set_visible_child(self.mainGrid)

    def onWindowClose(self, window):
        print("windows close")

    def quit(self, widget, _):
        print("quit")
        sys.exit()
    


#app = StreamControllerApp(application_id="com.core447.StreamController")
#app.run(sys.argv)
