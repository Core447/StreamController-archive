import json, os
class PluginBase():
    #List of all plugins
    plugins = {}
    pluginActions = []

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
        PluginBase.plugins[self.PLUGIN_NAME] = self
        pass

    def initActions(self) -> None:
        return

    def createUiConfigMenu(): #TODO: return Gtk Widget
        return
    
    def getPluginSetting(self, key):
        """
        Retrieves the value associated with the given key from the plugin settings.

        Parameters:
            key (str): The key to retrieve the value for.

        Returns:
            The value associated with the key if it exists, otherwise None.
        """
        #check if file exists
        pluginSettingsFilePath = os.path.join(self.PLUGIN_PATH, "pluginSettings.json")
        if not os.path.exists(pluginSettingsFilePath):
            pluginData = {}
        else:
            #load json
            with open(pluginSettingsFilePath) as file:
                pluginData = json.load(file)
        
        if key not in pluginData:
            return None
        return pluginData[key]
    
    def setPluginSetting(self, key, value):
        """
        Set a value for a plugin setting.

        Parameters:
            key (str): The key of the setting to be set.
            value (Any): The value to be set for the setting.

        Returns:
            None
        """
        #check if file exists
        pluginSettingsFilePath = os.path.join(self.PLUGIN_PATH, "pluginSettings.json")
        if not os.path.exists(pluginSettingsFilePath):
            pluginData = {}
        else:
            #load json
            with open(pluginSettingsFilePath) as file:
                pluginData = json.load(file)
        
        pluginData[key] = value

        #save file
        with open(pluginSettingsFilePath, 'w') as file:
            json.dump(pluginData, file, indent=4)

    def getButtonSetting(self, buttonCoords, pageName, key, actionIndex = 0):
        buttonSettingsFilePath = os.path.join(self.PLUGIN_PATH, "buttonSettings.json")
        buttonData = {}

        if os.path.exists(buttonSettingsFilePath):
            with open(buttonSettingsFilePath) as file:
                buttonData = json.load(file)

        if buttonData.get(pageName) and buttonData[pageName].get(buttonCoords) and buttonData[pageName][buttonCoords].get(key):
            return buttonData[pageName][buttonCoords][key].get(actionIndex)

        return None

    def setButtonSetting(self, buttonCoords, pageName, key, value, actionIndex = 0):
        buttonSettingsFilePath = os.path.join(self.PLUGIN_PATH, "buttonSettings.json")
        buttonData = {}

        if os.path.exists(buttonSettingsFilePath):
            with open(buttonSettingsFilePath) as file:
                buttonData = json.load(file)

        if pageName not in buttonData:
            buttonData[pageName] = {}
        if buttonCoords not in buttonData[pageName]:
            buttonData[pageName][buttonCoords] = {}
        if key not in buttonData[pageName][buttonCoords]:
            buttonData[pageName][buttonCoords][key] = {}

        buttonData[pageName][buttonCoords][key][actionIndex] = value

        with open(buttonSettingsFilePath, 'w') as file:
            json.dump(buttonData, file, indent=4)


