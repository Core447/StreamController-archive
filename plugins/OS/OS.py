from Action import ActionBase
from PluginBase import PluginBase

from time import sleep
import json
from gi.repository import Gtk, Adw, Gdk
import subprocess
import os
import threading

class RunCommand(ActionBase):
    ACTION_NAME = "run_command"
    ALLOW_USER_IMAGE = True
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.pluginBase = pluginBase

        # self.controller = None
        # self.deck = None
        self.buttonJsonName = None
        self.actionIndex = None
        self.pageName = None

        self.commandEntry = None
                    
    def onKeyDown(self, controller, deck, pageName, keyIndex, actionIndex):
        command = None
        # Check command entry has already been created
        if self.commandEntry == None:
            command = self.pluginBase.getButtonSetting(controller.getJsonKeySyntaxByIndex(keyIndex), pageName, "command", actionIndex)
        # Check if command is inserted in entry box
        if command == None:
            command = self.commandEntry.get_text()
            # if self.commandEntry.get_text() == "":
        

        print(command)
        #TODO: run in thread
        # os.system(command)
        self.runCommandInThread(command)
    
    def tick(self, controller, deck, pageName, keyIndex, actionIndex):
        """
        This function is called every second to allow constant updating
        """

    def getInitialJson(self):
        return {'captions': [], 'default-image': None, 'background': [0, 0, 0], 'actions': ['OS:run_command']}
    
    def getConfigLayout(self, pageName, buttonJsonName, actionIndex):
        configBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=10, margin_end=10)

        self.header = Gtk.Label(label="Run Command:", css_classes=["header"], xalign=0)
        self.commandEntry = Gtk.Entry(placeholder_text="Enter Command", margin_top=5)
        self.commandEntry.connect("changed", self.onEntryBoxChange)

        configBox.append(self.header)
        configBox.append(self.commandEntry)

        # Set variables for later use
        self.pageName = pageName
        self.buttonJsonName = buttonJsonName
        self.actionIndex = actionIndex


        # Get saved command and put it into entry
        command = self.pluginBase.getButtonSetting(self.buttonJsonName, self.pageName, "command", self.actionIndex)
        if command is None: command = ""
        self.commandEntry.set_text(command)

        return configBox
    
    def onEntryBoxChange(self, entry):
        if self.actionIndex == None:
            # Has not been set (yet)
            return
        self.pluginBase.setButtonSetting(self.buttonJsonName, self.pageName, "command", entry.get_text(), self.actionIndex)
        

    
    #custom functions
    def runCommandInThread(self, command: str):
        if not isinstance(command, str):
            raise ValueError("Command must be a string")
        
        thread = threading.Thread(target=self.runCommand, args=(command,))
        thread.start()

    def runCommand(self, command: str):
        if not isinstance(command, str):
            raise ValueError("Command must be a string")
        os.system(command)


#The plugin class
class OS(PluginBase):
    PLUGIN_NAME = "OS"
    PLUGIN_PATH = os.path.dirname(os.path.relpath(__file__)) #set path to plugin
    pluginActions = []
    def __init__(self):
        super().__init__()
        self.initActions()
        return
    
    def initActions(self) -> None:
        self.pluginActions.append(RunCommand(self))
        return
    
#Init the plugin
OS()