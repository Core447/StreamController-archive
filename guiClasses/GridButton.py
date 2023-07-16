from gi.repository import Gtk, Gdk, Gio
from guiClasses.ConfigButton import ConfigButton
from guiClasses.ActionButton import ActionButton
import json
from controller import ASSETS_PATH
import os
from time import sleep
class GridButton(Gtk.Button):
    def __init__(self, app, grid: Gtk.Grid, row: int, column: int):
        super().__init__()
        self.app = app
        self.grid = grid
        self.gridPosition = (row, column)
        self.set_css_classes(["gridButton"])

        self.set_focusable(True)
        self.set_focus_on_click(True)
        self.set_can_focus(True)
        self.set_can_target(True)
        grid.attach(self, column, row, 1, 1) 
        self.eventTag = None
        
        self.loadedActionConfigLayout = None

        #Drag and drop
        #button.connect('drag_begin', self.dragBegin )

        #button.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        #button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)

        
        dnd = Gtk.DropTarget.new(ActionButton, Gdk.DragAction.COPY)
        dnd.connect('drop', self.on_dnd_drop)
        #dnd.connect('accept', self.on_dnd_accept)
        #dnd.connect('enter', self.on_dnd_enter)
        #dnd.connect('motion', self.on_dnd_motion)
        #dnd.connect('leave', self.on_dnd_leave)
        self.add_controller(dnd)     

        #focus controller
        self.focusCtrl = Gtk.EventControllerFocus().new()
        self.focusCtrl.connect("enter", self.onEntryFocusIn)
        self.add_controller(self.focusCtrl)

        #click controller
        self.clickCtrl = Gtk.GestureClick().new()
        self.clickCtrl.connect("pressed", self.onRightMouseButtonPress)
        self.clickCtrl.set_button(3) #right mouse button
        self.add_controller(self.clickCtrl)
        
        self.image = Gtk.Image(hexpand=True, vexpand=True)
        self.image.clear()
        self.set_child(self.image)
  
    def on_dnd_drop(self, drop_target, value, x, y):
        #print(f'in on_dnd_drop(); value={value}, x={x}, y={y}')
        #print(list(value))
        if isinstance(value, ActionButton):
            #ActionButton got dropped
            self.addActionToGrid(value)

        return True

    def on_dnd_accept(self, drop, user_data):
        print(type(user_data))
        return True

    def on_dnd_enter(self, drop_target, x, y):
        print(f'in on_dnd_enter(); drop_target={drop_target}, x={x}, y={y}')
        return Gdk.DragAction.COPY

    def on_dnd_motion(self, drop_target, x, y):
        print(f'in on_dnd_motion(); drop_target={drop_target}, x={x}, y={y}')
        return Gdk.DragAction.COPY

    def on_dnd_leave(self, user_data):
        print(f'in on_dnd_leave(); user_data={user_data}')

    


    def addActionToGrid(self, actionButton: ActionButton):
        self.addActionByEventTag(actionButton.eventTag)  
       

    def addActionByEventTag(self, eventTag: str):
        pageName = self.app.communicationHandler.deckController[0].loadedPage
        buttonInitialJson = self.app.communicationHandler.actionIndex[eventTag].getInitialJson()

        jsonButtonCoords = f"{self.gridPosition[0]}x{self.gridPosition[1]}"
        print(jsonButtonCoords)
        newButtonJson = {jsonButtonCoords: buttonInitialJson}
        
        pageData = self.app.communicationHandler.deckController[0].loadedPageJson

        pageData["buttons"].update(newButtonJson)

        with open(os.path.join("pages", self.app.communicationHandler.deckController[0].loadedPage + ".json"), 'w') as file:
            json.dump(pageData, file, indent=4)

        #get first deck #TODO: use the selected deck
        deckController = self.app.communicationHandler.deckController[0]
        #print(deckController.)
        print(f"loading Page: {pageName}")
        deckController.loadPage(pageName, True)

        self.eventTag = eventTag


    def clearActionConfigBox(self):
        self.app.leftSideGrid.remove(self.app.actionConfigBox)
        self.app.actionConfigBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, margin_bottom=10)
        self.app.leftSideGrid.append(self.app.actionConfigBox)

        return
        #FIXME: the code below would be cleaner but is not working, no idea why
        #clear all children in actionConfigBox
        while(self.app.actionConfigBox.get_first_child() != None):
            self.app.actionConfigBox.remove(self.get_first_child())  

    def onEntryFocusIn(self, event):
        self.clearActionConfigBox()

        pageData = self.app.communicationHandler.deckController[0].loadedPageJson
        jsonButtonCoords = f"{self.gridPosition[0]}x{self.gridPosition[1]}"
        if jsonButtonCoords not in pageData["buttons"]:
            #no action assigned
            return
        
        actionKey = pageData["buttons"][jsonButtonCoords]["actions"]["on-press"][0] #TODO: Find solution to show not only the first, maybe only allow one action and seperate multiactions completely
        if actionKey not in self.app.communicationHandler.actionIndex:
            return
        
        if not hasattr(self.app.communicationHandler.actionIndex[actionKey], "getConfigLayout"):
            #no config layout defined
            return
        actionConfigLayout = self.app.communicationHandler.actionIndex[actionKey].getConfigLayout()
        if actionConfigLayout == None:
            #no config layout defined
            return
        
        #add seperator
        self.app.actionConfigBox.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, margin_bottom=0))

        #add label
        self.app.actionConfigBox.append(Gtk.Label(label=actionKey, css_classes=["action-config-header"], xalign=0, margin_start=5))
    
        #add configLayout from action
        self.app.actionConfigBox.append(actionConfigLayout)

    def onRightMouseButtonPress(self, widget, nPress, x, y):
        contextMenu = GridButtonContextMenu(self.app, self)
        contextMenu.popover.popup()

    def removeAction(self):
        pageData = self.app.communicationHandler.deckController[0].loadedPageJson
        jsonButtonCoords = f"{self.gridPosition[0]}x{self.gridPosition[1]}"

        if jsonButtonCoords not in pageData["buttons"]:
            #button is not configured
            return
        
        del pageData["buttons"][jsonButtonCoords]
        #save new page json
        with open(os.path.join("pages", self.app.communicationHandler.deckController[0].loadedPage + ".json"), 'w') as file:
            json.dump(pageData, file, indent=4)

        self.app.communicationHandler.deckController[0].loadPage(self.app.communicationHandler.deckController[0].loadedPage, True)

        self.eventTag = None


    
        
class GridButtonContextMenu:
    copiedEventTag = None
    def __init__(self, app, gridButton: GridButton):
        self.app = app
        self.gridButton = gridButton
        self.buildContextMenu()
    
    def buildContextMenu(self):
        # Create the menus
        self.mainMenu = Gio.Menu.new()
        self.copyPasteMenu = Gio.Menu.new()
        self.removeMenu = Gio.Menu.new()

        # Create actions for each menu item
        cut_action = Gio.SimpleAction.new("cut", None)
        copy_action = Gio.SimpleAction.new("copy", None)
        paste_action = Gio.SimpleAction.new("paste", None)
        remove_action = Gio.SimpleAction.new("remove", None)

        cut_action.connect("activate", self.cut)
        copy_action.connect("activate", self.copy)
        paste_action.connect("activate", self.paste)
        remove_action.connect("activate", self.remove)

        self.app.add_action(cut_action)
        self.app.add_action(copy_action)
        self.app.add_action(paste_action)
        self.app.add_action(remove_action)

        # Append menu items to the copyPasteMenu and removeMenu
        self.copyPasteMenu.append("Cut", "app.cut")
        self.copyPasteMenu.append("Copy", "app.copy")
        self.copyPasteMenu.append("Paste", "app.paste")
        self.removeMenu.append("Remove", "app.remove")

        # Append the copyPasteMenu and removeMenu to the mainMenu
        self.mainMenu.append_section("Edit", self.copyPasteMenu)
        self.mainMenu.append_section("Remove", self.removeMenu)

        # Create the popover
        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(self.mainMenu)
        self.popover.set_parent(self.gridButton)
        self.popover.set_has_arrow(False)


    def cut(self, action, param):
        #store eventTag
        GridButtonContextMenu.copiedEventTag = self.gridButton.eventTag
        #remove action
        self.gridButton.removeAction()
        self.gridButton.clearActionConfigBox()
        

    def remove(self, action, param):
        self.gridButton.removeAction()
        self.gridButton.clearActionConfigBox()

    def copy(self, action, param):
        GridButtonContextMenu.copiedEventTag = self.gridButton.eventTag #store eventTag

    def paste(self, action, param):
        self.gridButton.addActionByEventTag(GridButtonContextMenu.copiedEventTag)