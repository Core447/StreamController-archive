from Action import ActionBase
from PluginBase import PluginBase

from time import sleep
from pynput.keyboard import Key, Controller

class PausePlay(ActionBase):
    ACTION_NAME = "pauseplay"
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.pluginBase = pluginBase
    def onKeyDown(self, controller, deck, keyIndex):
        print("pressing")
        self.pluginBase.keyboard.press(Key.media_play_pause)
        sleep(0.1)
        self.pluginBase.keyboard.release(Key.media_play_pause)
        controller.loadButton("0x0", "Pressed.png", [], "Roboto-Regular.ttf")
        return
    def onKeyUp(self, controller, deck, keyIndex):
        #self.pluginBase.keyboard.release(Key.pause)
        controller.loadButton("0x0", "Exit.png", [], "Roboto-Regular.ttf")
        return
    
class Next(ActionBase):
    ACTION_NAME = "next"
    def __init__(self, pluginBase: PluginBase):
        super().__init__()
        self.pluginBase = pluginBase
    def onKeyDown(self, controller, deck, keyIndex):
        print("next")
        return

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


