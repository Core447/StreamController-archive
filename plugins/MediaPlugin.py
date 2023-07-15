from Action import ActionBase
from PluginBase import PluginBase

from time import sleep
from pynput.keyboard import Key, Controller
import json
from gi.repository import Gtk, Adw, Gdk

class PausePlay(ActionBase):
    ACTION_NAME = "pauseplay"
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.pluginBase = pluginBase
    def onKeyDown(self, controller, deck, keyIndex):
        self.pluginBase.keyboard.press(Key.media_play_pause)
        sleep(0.1)
        self.pluginBase.keyboard.release(Key.media_play_pause)
        controller.loadButton(keyIndex, "Harold.jpg", [[{'text': 'Pressed', 'font-size': 12, 'text-location': 0.5}]], "Roboto-Regular.ttf")
        return
    def onKeyUp(self, controller, deck, keyIndex):
        #self.pluginBase.keyboard.release(Key.pause)
        return
    
    def getInitialJson(self):
        return {'captions': [[{'text': 'Pause', 'font-size': 12, 'text-location': 0.5}]], 'default-image': 'Exit.png', 'background': [0, 0, 0], 'actions': {'on-press': ['Media:pauseplay'], 'on-release': []}}
    
    def getConfigLayout(self):
        return Gtk.Button(label="Pause config")
    
    #custom functions
    
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


