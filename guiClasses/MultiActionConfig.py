from gi.repository import Gtk, Gdk
from guiClasses.ActionButton import ActionButton #TODO: Remove unused import
from copy import copy
import os, json
class MultiActionConfig(Gtk.Box):
    def __init__(self, app) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.app = app
        self.actionBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, hexpand=True, vexpand=True, homogeneous=True)
        self.actionBox.add_css_class("linked")

        #add info grid
        self.infoGrid = Gtk.Grid(margin_start=5, margin_bottom=5, margin_top=5)
        self.append(self.infoGrid)

        #add title
        self.title = Gtk.Label(label="Multi Action Config", css_classes=["multi-action-config-title"])
        self.infoGrid.attach(self.title, 1, 0, 1, 1)

        #add seperator
        self.append(Gtk.Separator())

        #add actionBox
        self.append(self.actionBox)

        #add back button to header
        self.backButton = Gtk.Button(icon_name="go-previous-symbolic")
        self.backButton.connect("clicked", self.onBack)
        self.app.header.pack_start(self.backButton)
        self.backButton.set_visible(False) #hide back button

        self.preview = MultiActionConfigButtonDropPreview("preview")
        self.preview.set_visible(False)
        self.actionBox.append(self.preview)

    def addActionButton(self, action):
        label = self.app.communicationHandler.actionIndex[action].ACTION_NAME
        eventTag = self.app.communicationHandler.actionIndex[action].pluginBase.PLUGIN_NAME + ":" + label
        self.actionBox.append(MultiActionConfigButton(self.app, self, label, eventTag))

    def loadFromButton(self, gridButton):
        #check if there are any actions
        self.gridButton = gridButton
        actions = self.gridButton.actions
        if actions == None: return

        self.clearAllLoadedButtons()
        for action in actions:
            self.addActionButton(action)

        self.app.leftStack.set_visible_child(self)
        self.backButton.set_visible(True)
        
    def clearAllLoadedButtons(self):
        while self.actionBox.get_first_child() != None:
            self.actionBox.remove(self.actionBox.get_first_child())
        self.actionBox.append(self.preview)
        

    def onBack(self, widget):
        self.app.leftStack.set_visible_child_name("main")
        self.backButton.set_visible(False)


class MultiActionConfigButtonDropPreview(Gtk.Button):
    def __init__(self, label):
        super().__init__(label=label, height_request=75, width_request=500)
        self.set_opacity(0.5)
        self.set_sensitive(False)


class MultiActionConfigButton(Gtk.Button):
    def __init__(self, app, multiActionConfig: MultiActionConfig, label, eventTag) -> None:
        super().__init__(label=label, height_request=75, width_request=500)
        self.app = app
        self.multiActionConfig = multiActionConfig
        self.label = label,
        self.eventTag = eventTag

        self.createDnd()

        

    #Drag and drop
    def createDnd(self):
        #create all elements needed for drag and drop
        dndSource = Gtk.DragSource()
        dndTarget = Gtk.DropTarget.new(MultiActionConfigButton, Gdk.DragAction.COPY)

        dndSource.set_actions(Gdk.DragAction.COPY)
        dndSource.connect('prepare', self.on_dnd_prepare)
        dndSource.connect('drag-begin', self.on_dnd_begin)
        dndSource.connect('drag-end', self.on_dnd_end)
        #drop
        dndTarget.connect('drop', self.on_dnd_drop)
        dndTarget.connect('motion', self.on_dnd_motion)
        self.add_controller(dndSource)
        self.add_controller(dndTarget)

    def on_dnd_prepare(self, drag_source, x, y):
        print(f'in on_dnd_prepare(); drag_source={drag_source}, x={x}, y={y}')
        self.multiActionConfig.preview.set_label(self.get_label())
       
        drag_source.set_icon(
            Gtk.WidgetPaintable.new(self),
            self.get_width() / 2, self.get_height() / 2
        )
        print(f"content: {type(self)}, -> {self}")
        content = Gdk.ContentProvider.new_for_value(self)
        return content

    def on_dnd_begin(self, drag_source, data):
        content = data.get_content()
        print(f'in on_dnd_begin(); drag_source={drag_source}, data={data}, content={content}')

    def on_dnd_end(self, drag, drag_data, flag):
        print(f'in on_dnd_end(); drag={drag}, drag_data={drag_data}, flag={flag}')
        self.multiActionConfig.preview.set_visible(False)
        pass

    #drop
    def on_dnd_drop(self, drop_target, value, x, y):
        #print(f'in on_dnd_drop(); value={value}, x={x}, y={y}')
        print(f"dropped onto button with y:{self.get_allocation().y}, at: {y}")
        

        #self.multiActionConfig.actionBox.reorder_child_after(self, value)
        #self.set_opacity(0.5)

        if isinstance(value, MultiActionConfigButton):
            #MultiActionConfigButton got dropped
            if y < self.get_allocation().height/2:
                print("top")
            else:
                print("buttom")
            pass


        #print(self.multiActionConfig.actionBox.get_first_child().get_label())
        #self.multiActionConfig.gridButton.actions = ["action1", "action2", "action3"]

        self.multiActionConfig.gridButton.actions = []

        alreadyHadPreview = False

        print("label")
        child = self.multiActionConfig.actionBox.get_first_child() 
        while True:
            if child == None: break
            if child == self.multiActionConfig.preview:
                if alreadyHadPreview:
                    break
                alreadyHadPreview = True
                child = child.get_next_sibling()
                continue
            print(child.eventTag)
            self.multiActionConfig.gridButton.actions.append(child.eventTag)
            child = child.get_next_sibling()

        #save to page json
        pageName = self.app.communicationHandler.deckController[0].loadedPage
        pageData = self.app.communicationHandler.deckController[0].loadedPageJson
        buttonPosition = f"{self.multiActionConfig.gridButton.gridPosition[0]}x{self.multiActionConfig.gridButton.gridPosition[1]}"

        pageData["buttons"][buttonPosition]["actions"] = self.multiActionConfig.gridButton.actions

        with open(os.path.join("pages", pageName + ".json"), 'w') as file:
            json.dump(pageData, file, indent=4)
            

        return True
    def on_dnd_motion(self, drop_target, x, y):
        if not self.multiActionConfig.preview.get_visible():
            self.multiActionConfig.preview.set_visible(True)
        if y < self.get_allocation().height/2:
            print("top")
            self.multiActionConfig.actionBox.reorder_child_after(self, self.multiActionConfig.preview)
        else:
            print("buttom")
            self.multiActionConfig.actionBox.reorder_child_after(self.multiActionConfig.preview, self)
        pass
        print(f'in on_dnd_motion(); drop_target={drop_target}, x={x}, y={y}')
        print("position:")
        print(self.get_allocation().y)
        return Gdk.DragAction.COPY
    
