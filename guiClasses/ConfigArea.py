from gi.repository import Gtk, Gdk, Gio
from guiClasses.ConfigButton import ConfigButton
from guiClasses.ActionButton import ActionButton
import json
from controller import ASSETS_PATH
import os
import shutil

class ConfigArea(Gtk.Box):
    def __init__(self, app, inMultiAction = False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=True, margin_bottom=5, homogeneous=False)
        self.app = app
        self.inMultiAction = inMultiAction

        self.activeGridButton = None

        self.build()
        self.hide()

    def build(self):
        # Separator
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        # Main box
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        self.append(self.mainBox)

        self.imageConfigBox = ImageConfigBox(self.app, self)
        self.mainBox.append(self.imageConfigBox)

        # Separator
        self.mainBox.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        
        self.actionConfigBox = ActionConfigBox(self.app)
        self.mainBox.append(self.actionConfigBox)

    def update(self):
        self.imageConfigBox.button.update()

    # def clear(self):
    #     while self.get_first_child() is not None:
    #         self.remove(self.get_first_child())

    def showConfig(self, inMultiAction = False):
        self.show()




class ActionConfigBox(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=True, margin_top=25, margin_start=15, margin_bottom=15, margin_end=15)
        self.app = app

    def clear(self):
        while self.get_first_child() != None:
            self.remove(self.get_first_child())

    def load(self, pageName, eventTag, buttonJsonName, actionIndex):
        self.clear()

        
        action = self.app.communicationHandler.actionIndex[eventTag]
        if not hasattr(action, "getConfigLayout"):
            return
        configLayout = action.getConfigLayout(pageName, buttonJsonName, actionIndex)
        self.append(configLayout)


class ImageConfigBox(Gtk.Box):
    def __init__(self, app, configArea):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, margin_top=10, margin_start=10)
        self.app = app
        self.configArea = configArea

        self.build()

    def build(self):
        self.button = ImageEditButton(self.configArea)
        self.append(self.button)


class ImageEditButton(Gtk.Button):
    def __init__(self, configArea: ConfigArea):
        super().__init__(css_classes=["gridButton"], hexpand=False, vexpand=False, margin_start=15, margin_bottom=15, margin_end=15, margin_top=15)
        self.configArea = configArea

        self.image = Gtk.Image(hexpand=True, vexpand=True)
        self.set_child(self.image)

        self.initDnd()
        self.initGesture()

    def initGesture(self):
        self.clickCtrl = Gtk.GestureClick().new()
        self.clickCtrl.connect("pressed", self.onRightMouseClick)
        self.clickCtrl.set_button(3) # Right mouse button
        self.add_controller(self.clickCtrl)

    def initDnd(self):
        self.dnd = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        self.dnd.connect("drop", self.onDndDrop)
        self.dnd.connect("accept", self.onDndAccept)
        self.add_controller(self.dnd)

    def onDndAccept(self, drop, userData):
        return True

    def onDndDrop(self, dropTarget, value, x, y):
        path = value.get_path()
        # Check if file is an image
        if os.path.splitext(path)[-1] not in [".png", ".jpg", ".jpeg"]:
            self.wrongTypeDialog = Gtk.MessageDialog(buttons=Gtk.ButtonsType.OK, message_type=Gtk.MessageType.ERROR, text="Invalid file type")
            self.wrongTypeDialog.connect("response", self.onWrongTypeDialogResponse)
            self.wrongTypeDialog.show()
            return False
        
        # File is an image
        dstPath = self.getDstImagePath(path)
        # Copy file into internal folder
        shutil.copy(path, dstPath)
        # Show image on button
        self.image.set_from_file(dstPath)
        # Upadate the page json
        self.addImageToPageJson(dstPath)
        # Update page
        self.configArea.app.communicationHandler.deckController[0].loadPage(self.configArea.app.communicationHandler.deckController[0].loadedPage, True)

    
    def onWrongTypeDialogResponse(self, dialog, response):
        self.wrongTypeDialog.destroy()

    def getDstImagePath(self, srcPath):
        # Get the file name
        file = os.path.basename(srcPath)
        # Get all files in the folder "userImages"
        dir = os.listdir("userImages")
        dir = [f for f in dir if os.path.isfile(os.path.join("userImages", f))]

        ## Get the name for the file
        # Check if the given file name already exists in the directory
        if file not in dir:
            copyName = file
        else:
            # Extract the base name and numeric suffix
            splittedFileName = os.path.splitext(file)[0].split("_")
                
            # Find all files with the same base name and add the numeric suffix to this list
            numbers = []
            for fileName in dir:
                if os.path.splitext(fileName)[0].split("_")[0] == splittedFileName[0]:
                    if os.path.splitext(fileName)[0].split("_")[-1].isnumeric():
                        numbers.append(int(os.path.splitext(fileName)[0].split("_")[-1]))

            # Sort the list of numeric suffixes in ascending order
            numbers.sort()
            
            if splittedFileName[-1].isnumeric():
                # The file already had an number suffix, increment it
                copyName = file[:-len(file.split("_")[-1])] + str(numbers[-1] + 1) + os.path.splitext(file)[-1]
            else:
                # The file did not have an number suffix, add it
                copyName = os.path.splitext(file)[0] + "_1" + os.path.splitext(file)[-1]

        print(copyName)
        return os.path.join("userImages", copyName)

    
    def addImageToPageJson(self, imagePath):
        # active page json path
        pagePath = os.path.join("pages", self.configArea.app.communicationHandler.deckController[0].loadedPage + ".json")
        # Open active page json
        with open(pagePath, 'r') as file:
            pageData = json.load(file)
        # Set new image
        pageData["buttons"][f"{self.configArea.activeGridButton.gridPosition[0]}x{self.configArea.activeGridButton.gridPosition[1]}"]["custom-image"] = imagePath
        # Save page json
        with open(pagePath, 'w') as file:
            json.dump(pageData, file, indent=4)

    def update(self):
        gridButtonCords = self.configArea.activeGridButton.gridPosition
        pageJson = self.configArea.app.communicationHandler.deckController[0].loadedPageJson

        buttonsJsonTag = f"{gridButtonCords[0]}x{gridButtonCords[1]}"
        if buttonsJsonTag in pageJson["buttons"]:
            if "custom-image" in pageJson["buttons"][buttonsJsonTag]:
                self.image.set_from_file(pageJson["buttons"][buttonsJsonTag]["custom-image"])
                return
            
        self.image.clear()

    def onRightMouseClick(self, widget, nPress, x, y):
        self.contextMenu = ImageEditButtonContextMenu(self)
        self.contextMenu.popup()
        # self.set_action_name("button.remove")

    def removeCustomImage(self, actin, param):
        self.image.clear()
        # Remove image from json
        pageJson = self.configArea.app.communicationHandler.deckController[0].loadedPageJson
        del pageJson["buttons"][f"{self.configArea.activeGridButton.gridPosition[0]}x{self.configArea.activeGridButton.gridPosition[1]}"]["custom-image"]

        # Save page json
        pagePath = os.path.join("pages", self.configArea.app.communicationHandler.deckController[0].loadedPage + ".json")
        with open(pagePath, 'w') as file:
            json.dump(pageJson, file, indent=4)

        self.configArea.app.communicationHandler.deckController[0].realoadPage()



class ImageEditButtonContextMenu(Gtk.PopoverMenu):
    def __init__(self, imageEditButton: ImageEditButton):
        super().__init__()
        self.imageEditButton = imageEditButton
        self.build()

    def build(self):
        # Create the menu
        self.menu = Gio.Menu.new()
        # Create the menu item
        self.removeAction = Gio.SimpleAction.new("removeCustomImage", None)
        # Connect action
        self.removeAction.connect("activate", self.imageEditButton.removeCustomImage)

        self.imageEditButton.configArea.app.add_action(self.removeAction)

        self.menu.append("Remove", "app.removeCustomImage")

        self.set_menu_model(self.menu)
        self.set_parent(self.imageEditButton)
        self.set_has_arrow(False)