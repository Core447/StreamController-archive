import json, os, shutil

class InfoSaver:
    def __init__(self) -> None:
        pass

    def loadInfos(self) -> dict:
        # Return empty dict if file does not exist
        if not os.path.exists("plugins/pluginInfos.json"):
            return {}
        try:
            # Load json
            with open("plugins/pluginInfos.json", "r") as file:
                infos = json.load(file)
            return infos
        except ValueError:
            print("Error while loading plugins/pluginInfos.json")
            print("Copying plugins/pluginInfos.json to plugins/pluginInfos.json.backup and generating new one...")
            # Make backup in case the file contained important information
            shutil.copy2("plugins/pluginInfos.json", "plugins/pluginInfos.json.backup")

            # Return empty dict
            return {}
    
    def saveInfos(self, infos: dict) -> None:
        # Save json
        with open("plugins/pluginInfos.json", "w") as file:
            json.dump(infos, file, indent=4)