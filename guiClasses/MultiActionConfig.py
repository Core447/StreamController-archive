from gi.repository import Gtk, Gdk, Gio
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


        self.initDrop()

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

    #drop functions
    def initDrop(self):
        self.dndTarget = Gtk.DropTarget.new(MultiActionConfigButton, Gdk.DragAction.COPY)
        self.dndTarget.connect("drop", self.onDndDrop)
        self.dndTarget.connect("motion", self.onDndMotion)
        self.add_controller(self.dndTarget)

    def onDndDrop(self, drop_target, value, x, y):
        #self.actionBox.get_first_child().saveConfig()
        return True

    def onDndMotion(self, drop_target, x, y):
        firstButton = self.actionBox.get_first_child()
        lastButton = self.actionBox.get_last_child()

        self.preview.set_visible(True)
        if y < (self.actionBox.get_allocation().y + (firstButton.get_allocation().height * (self.getNRealActions() - 1)/2)):
            #mouse on top of actions
            self.actionBox.reorder_child_after(self.preview, firstButton)
            self.actionBox.reorder_child_after(firstButton, self.preview)
        elif y > ((lastButton.get_allocation().height * self.getNRealActions() - 1)/2 + (lastButton.get_allocation().height * (self.getNRealActions() - 1))):
            #mouse below actions
            self.actionBox.reorder_child_after(self.preview, lastButton)




        return Gdk.DragAction.COPY
    
    def getNRealActions(self) -> int:
        child = self.actionBox.get_first_child()
        nChildren = 0
        while True:
            if child == None: break

            nChildren += 1

            if child == self.actionBox.get_last_child(): break
            child = child.get_next_sibling()

        return nChildren


class MultiActionConfigButtonDropPreview(Gtk.Button):
    def __init__(self, label):
        super().__init__(label=label, height_request=75, width_request=500)
        self.set_opacity(0.5)
        self.set_sensitive(False)


class MultiActionConfigButton(Gtk.Button):
    def __init__(self, app, multiActionConfig: MultiActionConfig, label, eventTag) -> None:
        #super().__init__(label=label, height_request=75, width_request=500)
        super().__init__(height_request=75, width_request=500)
        self.app = app
        self.multiActionConfig = multiActionConfig
        self.label = label,
        self.eventTag = eventTag

        self.createButton()
        self.createDnd()

        #click controller
        self.clickCtrl = Gtk.GestureClick().new()
        self.clickCtrl.connect("pressed", self.onRightMouseButtonPress)
        self.clickCtrl.set_button(3) #right mouse button
        self.add_controller(self.clickCtrl)

    def createButton(self):
        self.mainGrid = Gtk.Grid(margin_start=5, margin_bottom=5, margin_top=5, hexpand=True, vexpand=True)
        self.rightBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, margin_top=7.5)
        self.eventLabel = Gtk.Label(label="".join(self.eventTag.split(":")[1:]), margin_end=35)
        self.categoryLabel = Gtk.Label(label=self.eventTag.split(":")[0], margin_end=35, css_classes=["category-label"])
        self.icon = Gtk.Image(pixel_size=25, margin_end=10, margin_top=12.5, margin_bottom=12.5, file="")

        self.rightBox.append(self.eventLabel)
        self.rightBox.append(self.categoryLabel)
        self.mainGrid.attach(self.icon, 0, 0, 1, 1)
        self.mainGrid.attach(self.rightBox, 1, 0, 1, 1)
        self.set_child(self.mainGrid)

    def saveConfig(self):
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
        self.multiActionConfig.preview.set_label(self.eventLabel.get_label())
        self.set_visible(False)
       
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
        self.multiActionConfig.actionBox.reorder_child_after(self, self.multiActionConfig.preview)
        self.set_visible(True)
        self.saveConfig()
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
                #print("top")
                pass
            else:
                #print("buttom")
                pass
            pass


        #print(self.multiActionConfig.actionBox.get_first_child().get_label())
        #self.multiActionConfig.gridButton.actions = ["action1", "action2", "action3"]

        #self.saveConfig()
            

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
    
    def onRightMouseButtonPress(self, widget, nPress, x, y):
        contextMenu = MultiActionConfigButtonContextMenu(self.app, self)
        contextMenu.popover.popup()
    
class MultiActionConfigButtonContextMenu:
    def __init__(self, app, configButton):
        super().__init__()
        self.app = app
        self.configButton = configButton
        self.buildContextMenu()

    def buildContextMenu(self):
    # Create the menus
        self.mainMenu = Gio.Menu.new()
        self.moveMenu = Gio.Menu.new()
        self.copyPasteMenu = Gio.Menu.new()
        self.editMultiActionMenu = Gio.Menu.new()
        self.removeMenu = Gio.Menu.new()
        

        # Create actions for each menu item
        cutAction = Gio.SimpleAction.new("cut", None)
        copyAction = Gio.SimpleAction.new("copy", None)
        pasteBelowAction = Gio.SimpleAction.new("pasteBelow", None)
        removeAction = Gio.SimpleAction.new("remove", None)
        moveUpAction = Gio.SimpleAction.new("moveUp", None)
        moveDownAction = Gio.SimpleAction.new("moveDown", None)

        cutAction.connect("activate", self.cut)
        copyAction.connect("activate", self.copy)
        pasteBelowAction.connect("activate", self.pasteBelow)
        removeAction.connect("activate", self.remove)
        moveUpAction.connect("activate", self.moveUp)
        moveDownAction.connect("activate", self.moveDown)

        self.app.add_action(cutAction)
        self.app.add_action(copyAction)
        self.app.add_action(pasteBelowAction)
        self.app.add_action(removeAction)
        self.app.add_action(moveUpAction)
        self.app.add_action(moveDownAction)

        # Append menu items to the copyPasteMenu, removeMenu and editMultiMenu
        self.copyPasteMenu.append("Cut", "app.cut") #TODO: switch from app. to something else, to avoid conflicts with other events
        self.copyPasteMenu.append("Copy", "app.copy")
        self.copyPasteMenu.append("Paste below", "app.pasteBelow")
        self.removeMenu.append("Remove", "app.remove")
        self.moveMenu.append("Move Up", "app.moveUp")
        self.moveMenu.append("Move Down", "app.moveDown")

        # Append the copyPasteMenu and removeMenu to the mainMenu
        self.mainMenu.append_section("Move", self.moveMenu)
        self.mainMenu.append_section(None, self.copyPasteMenu)
        self.mainMenu.append_section(None, self.removeMenu)

        # Create the popover
        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(self.mainMenu)
        self.popover.set_parent(self.configButton)
        self.popover.set_has_arrow(False)


    def cut(self, action, param):
        pass

    def remove(self, action, param):
        self.configButton.multiActionConfig.actionBox.remove(self.configButton)
        self.configButton.saveConfig()

    def copy(self, action, param):
        MultiActionConfigButtonContextMenu.copiedEventTag = self.configButton.eventTag

    def pasteBelow(self, action, param):
        print(f"tag: {MultiActionConfigButtonContextMenu.copiedEventTag}")
        eventTag = MultiActionConfigButtonContextMenu.copiedEventTag
        newButton = MultiActionConfigButton(self.app, self.configButton.multiActionConfig,  "".join(eventTag.split(":")[1:]), eventTag)
        self.configButton.multiActionConfig.actionBox.append(newButton)

        #move newButton below clicked button
        self.configButton.multiActionConfig.actionBox.reorder_child_after(newButton, self.configButton)
        self.configButton.saveConfig()

    def moveUp(self, action, param):
        buttonOnTop = self.configButton.get_prev_sibling()
        self.configButton.multiActionConfig.actionBox.reorder_child_after(self.configButton, buttonOnTop)
        self.configButton.multiActionConfig.actionBox.reorder_child_after(buttonOnTop, self.configButton)
        self.configButton.saveConfig()

    def moveDown(self, action, param):
        buttonBelow = self.configButton.get_next_sibling()
        self.configButton.multiActionConfig.actionBox.reorder_child_after(self.configButton, buttonBelow)
        self.configButton.saveConfig()