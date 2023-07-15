from Action import ActionBase
from PluginBase import PluginBase

from time import sleep
from pynput.keyboard import Key, Controller
import json
from gi.repository import Gtk, Adw, Gdk
import subprocess
import os

class PausePlay(ActionBase):
    ACTION_NAME = "pauseplay"
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.PLUGIN_FOLDER = os.path.dirname(__file__) #set to the folder of the plugin
        self.pluginBase = pluginBase

        #check if playerctl is installed on the system
        self.playerctlAvailable = False
        if self.runShellCommand("type -p playerctl") != None:
            self.playerctlAvailable = True
        print(self.playerctlAvailable)

        self.oldMediaStatus = None
                    
    def onKeyDown(self, controller, deck, keyIndex):
        self.pluginBase.keyboard.press(Key.media_play_pause)
        sleep(0.1)
        self.pluginBase.keyboard.release(Key.media_play_pause)
        controller.loadButton(keyIndex, "Pressed.png", [[{'text': 'Pressed', 'font-size': 12, 'text-location': 0.5}]], "Roboto-Regular.ttf")
        return
    def onKeyUp(self, controller, deck, keyIndex):
        #self.pluginBase.keyboard.release(Key.pause)
        return
    
    def tick(self, controller, deck, keyIndex):
        """
        This function is called every second to allow constant updating
        """
        newMediaStatus = str(self.getMediaStatus()) #convert None to "None"
        print(newMediaStatus)
        if self.oldMediaStatus != newMediaStatus or True: #FIXME: if this statement is active only the first of all buttons with this function will be updated
            controller.loadButton(keyIndex, "", [[{'text': newMediaStatus, 'font-size': 12, 'text-location': 0.5}]], "Roboto-Regular.ttf")
            self.oldMediaStatus = newMediaStatus
        print(f"tick from on index: {keyIndex} is over")

    def getInitialJson(self):
        return {'captions': [[{'text': 'Pause', 'font-size': 12, 'text-location': 0.5}]], 'default-image': 'Exit.png', 'background': [0, 0, 0], 'actions': {'on-press': ['Media:pauseplay'], 'on-release': []}}
    
    def getConfigLayout(self):
        if self.playerctlAvailable:
            return
        return Gtk.Label(label="Please install playerctl on your system")
    
    #custom functions
    def runShellCommand(self, command):
        # Run the shell command and capture the output
        try:
            output = subprocess.check_output(command, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            return None        

        # Return the output as a string
        return output
    
    def getMediaStatus(self) -> str:
        return self.runShellCommand("playerctl status")
    
class Next(ActionBase):
    ACTION_NAME = "next"
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.pluginBase = pluginBase
    def onKeyDown(self, controller, deck, keyIndex):
        print("next")
        return
    def getInitialJson(self):
        return {'captions': [[{'text': 'Text', 'font-size': 12, 'text-location': 0.5}], [{'text': 'Text2', 'font-size': 12, 'text-location': 1}]], 'default-image': 'Exit.png', 'background': [0, 0, 0], 'actions': {'on-press': ['Media:next'], 'on-release': []}}


#The plugin class
class MediaPlugin(PluginBase):
    PLUGIN_NAME = "Media"
    #pluginActions = []
    def __init__(self):
        super().__init__()
        self.initActions()

        self.keyboard = Controller()
        return
    
    def initActions(self) -> None:
        self.pluginActions.append(PausePlay(self))
        self.pluginActions.append(Next(self))
        return
    
#Init the plugin
MediaPlugin()


