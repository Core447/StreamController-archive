import json, os
class PluginBase():
    #List of all plugins
    plugins = {}
    # pluginActions = []

    #Change these variables to match your plugin
    PLUGIN_NAME = ""
    PLUGIN_PATH = ""

    def __init__(self) -> None:
        if self.PLUGIN_NAME == "":
            raise ValueError("Please set PLUGIN_NAME for your plugin")
        if self.PLUGIN_PATH == "":
            raise ValueError("Please set PLUGIN_PATH for your plugin")
        if self.PLUGIN_NAME in PluginBase.plugins:
            raise ValueError(f"Plugin {self.PLUGIN_NAME} already exists")
        if not hasattr(self, "pluginActions"):
            raise ValueError(f"Plugin {self.PLUGIN_NAME}: You need to define the pluginActions list, having all your actions in it")
        PluginBase.plugins[self.PLUGIN_NAME] = self
        pass

    def initActions(self) -> None:
        return

    def createUiConfigMenu(): #TODO: return Gtk Widget
        return
    
    def getButtonSetting(self, buttonCoords: str, pageName: str, key, actionIndex = 0):
        """
        Retrieves the value associated with the given key from the plugin settings.

        Returns:
            The value associated with the key if it exists, otherwise None.
        """
        buttonSettingsFilePath = os.path.join(self.PLUGIN_PATH, "buttonSettings.json")
        buttonData = {}

        if os.path.exists(buttonSettingsFilePath):
            with open(buttonSettingsFilePath) as file:
                buttonData = json.load(file)

        if pageName not in buttonData:
            return None
        if buttonCoords not in buttonData[pageName]:
            return None
        if str(actionIndex) not in buttonData[pageName][buttonCoords]:
            return None
        return buttonData[pageName][buttonCoords][str(actionIndex)][key]
    
    
    
    def setButtonSetting(self, buttonCoords: str, pageName: str, key, value, actionIndex = 0):
        buttonSettingsFilePath = os.path.join(self.PLUGIN_PATH, "buttonSettings.json")
        buttonData = {}

        if os.path.exists(buttonSettingsFilePath):
            with open(buttonSettingsFilePath) as file:
                buttonData = json.load(file)

        if pageName not in buttonData:
            buttonData[pageName] = {}
        if buttonCoords not in buttonData[pageName]:
            buttonData[pageName][buttonCoords] = {}
        if str(actionIndex) not in buttonData[pageName][buttonCoords]:
            buttonData[pageName][buttonCoords][str(actionIndex)] = {}
        #if key not in buttonData[pageName][buttonCoords][actionIndex]:
        #    buttonData[pageName][buttonCoords][key][actionIndex] = {}
        buttonData[pageName][buttonCoords][str(actionIndex)][key] = value

        with open(buttonSettingsFilePath, 'w') as file:
            json.dump(buttonData, file, indent=4)