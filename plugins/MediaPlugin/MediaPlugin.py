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

        self.oldMediaStatus = None

        self.showCurrentMediaState = None
                    
    def onKeyDown(self, controller, deck, pageName, keyIndex, actionIndex):
        self.pluginBase.keyboard.press(Key.media_play_pause)
        sleep(0.1)
        self.pluginBase.keyboard.release(Key.media_play_pause)
        return
    
    def tick(self, controller, deck, pageName, keyIndex, actionIndex):
        """
        This function is called every second to allow constant updating
        """
        self.updateIcon(controller, deck, keyIndex)

    def getInitialJson(self):
        return {'captions': [], 'default-image': os.path.join(self.pluginBase.PLUGIN_PATH, "images", "stop.png"), 'background': [0, 0, 0], 'actions': ['Media:pauseplay']}
    
    def getConfigLayout(self, pageName, buttonJsonName, actionIndex):
        configBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        if not self.playerctlAvailable:
            configBox.append(Gtk.Label(label="Please install playerctl on your system"))
            return configBox
        configBox.append(Gtk.Label(label="You have playerctl installed on your system, you're good to go!"))

        #set vars
        self.configLayoutPageName = pageName
        self.configLayoutButtonJsonName = buttonJsonName
        self.configLayoutActionIndex = actionIndex

        #user preferences
        self.showCurrentCheck = Gtk.CheckButton(label="Show current media status")
        self.showOnPressCheck = Gtk.CheckButton(label="Show media action executed on press", group=self.showCurrentCheck)
        self.showCurrentCheck.connect("toggled", self.configRadioToggled)
        self.showOnPressCheck.connect("toggled", self.configRadioToggled)

        configBox.append(self.showCurrentCheck)
        configBox.append(self.showOnPressCheck)


        return configBox
    
    #custom functions
    def configRadioToggled(self, button):
        self.showCurrentMediaState = self.showCurrentCheck.get_active()
        self.pluginBase.setButtonSetting(self.configLayoutButtonJsonName, self.configLayoutPageName, "showCurrentMediaState", self.showCurrentMediaState, self.configLayoutActionIndex)

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

        pause = "pause.png" if self.showCurrentMediaState else "play.png"
        play = "play.png" if self.showCurrentMediaState else "pause.png"

        mediaStatus = str(self.getMediaStatus()) #convert None to "None"
        #load icons
        if mediaStatus == "Playing":
            controller.loadButton(keyIndex, os.path.join(self.pluginBase.PLUGIN_PATH, "images", play), [], "Roboto-Regular.ttf")
        elif mediaStatus == "Paused":
            controller.loadButton(keyIndex, os.path.join(self.pluginBase.PLUGIN_PATH, "images", pause), [], "Roboto-Regular.ttf")
        elif mediaStatus in ["No players found", "None"]:
            controller.loadButton(keyIndex, os.path.join(self.pluginBase.PLUGIN_PATH, "images", "stop.png"), [], "Roboto-Regular.ttf")
    
class Next(ActionBase):
    ACTION_NAME = "next"
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.pluginBase = pluginBase
    def onKeyDown(self, controller, deck, keyIndex, actionIndex):
        self.pluginBase.keyboard.press(Key.media_next)
        sleep(0.1)
        self.pluginBase.keyboard.release(Key.media_next)
        return
    def getInitialJson(self):
        return {'captions': [], 'default-image': os.path.join(self.pluginBase.PLUGIN_PATH, "images", "next.png"), 'background': [0, 0, 0], 'actions': ['Media:next']}


#The plugin class
class MediaPlugin(PluginBase):
    PLUGIN_NAME = "Media"
    PLUGIN_PATH = os.path.dirname(os.path.relpath(__file__)) #set path to plugin
    pluginActions = []
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


