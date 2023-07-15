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
        return
    def onKeyUp(self, controller, deck, keyIndex):
        self.updateIcon(controller, deck, keyIndex)
        return
    
    def tick(self, controller, deck, keyIndex):
        """
        This function is called every second to allow constant updating
        """
        self.updateIcon(controller, deck, keyIndex)



    def getInitialJson(self):
        return {'captions': [], 'default-image': os.path.join(self.pluginBase.PLUGIN_FOLDER, "images", "stop.png"), 'background': [0, 0, 0], 'actions': {'on-press': ['Media:pauseplay'], 'on-release': []}}
    
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
        return output.replace("\n", "")
    
    def getMediaStatus(self) -> str:
        return self.runShellCommand("playerctl status")
    
    def updateIcon(self, controller, deck, keyIndex: int):
        mediaStatus = str(self.getMediaStatus()) #convert None to "None"
        #load icons
        if mediaStatus == "Playing":
            controller.loadButton(keyIndex, os.path.join(self.pluginBase.PLUGIN_FOLDER, "images", "pause.png"), [], "Roboto-Regular.ttf")
        elif mediaStatus == "Paused":
            controller.loadButton(keyIndex, os.path.join(self.pluginBase.PLUGIN_FOLDER, "images", "play.png"), [], "Roboto-Regular.ttf")
        elif mediaStatus in ["No players found", "None"]:
            controller.loadButton(keyIndex, os.path.join(self.pluginBase.PLUGIN_FOLDER, "images", "stop.png"), [], "Roboto-Regular.ttf")
    
class Next(ActionBase):
    ACTION_NAME = "next"
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.pluginBase = pluginBase
    def onKeyDown(self, controller, deck, keyIndex):
        self.pluginBase.keyboard.press(Key.media_next)
        sleep(0.1)
        self.pluginBase.keyboard.release(Key.media_next)
        return
    def getInitialJson(self):
        return {'captions': [], 'default-image': os.path.join(self.pluginBase.PLUGIN_FOLDER, "images", "next.png"), 'background': [0, 0, 0], 'actions': {'on-press': ['Media:next'], 'on-release': []}}


#The plugin class
class MediaPlugin(PluginBase):
    PLUGIN_NAME = "Media"
    #pluginActions = []
    def __init__(self):
        super().__init__()
        self.initActions()
        self.PLUGIN_FOLDER = os.path.dirname(os.path.relpath(__file__)) #set to the folder of the plugin

        self.keyboard = Controller()
        return
    
    def initActions(self) -> None:
        self.pluginActions.append(PausePlay(self))
        self.pluginActions.append(Next(self))
        return
    
#Init the plugin
MediaPlugin()


