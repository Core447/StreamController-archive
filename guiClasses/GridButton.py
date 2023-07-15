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
        self.gridPosition = (row, column)
        self.set_css_classes(["gridButton"])

        self.set_focusable(True)
        self.set_focus_on_click(True)
        self.set_can_focus(True)
        self.set_can_target(True)
        grid.attach(self, column, row, 1, 1) 
        
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
        print(actionButton.eventTag)
        pageName = self.app.communicationHandler.deckController[0].loadedPage
        
        buttonInitialJson = self.app.communicationHandler.actionIndex[actionButton.eventTag].getInitialJson()
        jsonButtonCoords = f"{self.gridPosition[0]}x{self.gridPosition[1]}"
        print(jsonButtonCoords)
        newButtonJson = {jsonButtonCoords: buttonInitialJson}
        
        pageData = self.app.communicationHandler.deckController[0].loadedPageJson

        pageData["buttons"].update(newButtonJson)

        with open(os.path.join("pages", pageName + ".json"), 'w') as file:
            json.dump(pageData, file, indent=4)

        #get first deck #TODO: use the selected deck
        deckController = self.app.communicationHandler.deckController[0]
        #print(deckController.)
        print(f"loading Page: {pageName}")
        deckController.loadPage(pageName, True)

    def clearActionConfigBox(self):
        self.app.leftSideGrid.remove(self.app.actionConfigBox)
        self.app.actionConfigBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
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
        
        actionConfigLayout = self.app.communicationHandler.actionIndex[actionKey].getConfigLayout()
        if actionConfigLayout == None:
            #no config layout defined
            return
    
        #add configLayout from action
        self.app.actionConfigBox.append(actionConfigLayout)