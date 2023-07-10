class PluginBase():
    #List of all plugins
    plugins = {}
    pluginActions = []

    #Change these variables to match your plugin
    PLUGIN_NAME = ""

    def __init__(self) -> None:
        if self.PLUGIN_NAME == "":
            raise ValueError("Please set PLUGIN_NAME for your plugin")
        if self.PLUGIN_NAME in PluginBase.plugins:
            raise ValueError(f"Plugin {self.PLUGIN_NAME} already exists")
        PluginBase.plugins[self.PLUGIN_NAME] = self
        pass

    def initActions(self) -> None:
        return

    def createUiConfigMenu(): #TODO: return Gtk Widget
        return