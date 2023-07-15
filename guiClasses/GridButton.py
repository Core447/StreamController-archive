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

        grid.attach(self, column, row, 1, 1) 

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
        
        self.image = Gtk.Image(hexpand=True, vexpand=True)
        self.image.clear()
        self.set_child(self.image)

    #TODO: only accept ActionButtons    
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
        pageName = self.app.pageSelector.comboBox.get_child().get_text()

        #check if page exists
        pageFilePath = os.path.join("pages", pageName + ".json")
        if not os.path.exists(pageFilePath):
            raise FileNotFoundError(f"Page {pageName} does not exist")

        with open(pageFilePath) as file:
            pageData = json.load(file)
        #print(pageData)

        #button_data = {'position': '0x0', 'captions': [[{'text': 'New Button', 'font-size': 12, 'text-location': 0.5}], [{'text': 'New Button Text', 'font-size': 12, 'text-location': 1}]], 'default-image': 'NewButton.png', 'background': [0, 0, 0], 'actions': {'on-press': ['none'], 'on-release': ['none']}}
        #pageData['buttons'].update({button_data['position']: button_data})

        #if "0x0" in pageData["buttons"]:
        #    print("exists")

        buttonInitialJson = self.app.communicationHandler.actionIndex[actionButton.eventTag].getInitialJson()
        jsonButtonCoords = f"{self.gridPosition[0]}x{self.gridPosition[1]}"
        print(jsonButtonCoords)
        newButtonJson = {jsonButtonCoords: buttonInitialJson}
        pageData["buttons"].update(newButtonJson)

        with open(pageFilePath, 'w') as file:
            json.dump(pageData, file, indent=4)

        #get first deck #TODO: use the selected deck
        deckController = self.app.communicationHandler.deckController[0]
        #print(deckController.)
        print(f"loading Page: {pageName}")
        deckController.loadPage(pageName, True)