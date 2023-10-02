import threading, time, json, os, sys, importlib

sys.path.append("guiClasses/PluginStore")
from GitHubHelper import GitHubHelper

class StoreLoadingThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.githubHelper = GitHubHelper()

        # Load plugins json
        if os.path.exists("plugins/PluginsCacheInfos.json"):
            with open("plugins/PluginsCacheInfos.json", "r") as file:
                self.plugins = json.load(file)
        else:
            self.plugins = []
            # Reset Plugins.json which contains the current state of the cache
            if os.path.exists("plugins/Plugins.json"):
                os.remove("plugins/Plugins.json")
        self.ready = False

    def run(self):
        while not self.ready:
            self.downloadCache()

    def reloadCache(self):
        self.ready = False
        while not self.ready:
            self.downloadCache()
        self.ready = True

    def installUpdates(self):
        # Update local cache
        self.reloadCache()

        # Install updates
        changedPlugins = self.getChangedPlugins()
        for plugin in changedPlugins:
            print(plugin)
            continue

    def getChangedPlugins(self):
        oldPluginList, newPluginList = self.getJsons()
        if oldPluginList == None or newPluginList == None:
            return
        
        return self.getChanges(oldPluginList, newPluginList)

    def checkForUpdates(self) -> bool:
        # Update local cache
        self.reloadCache()

        if self.plugins == []:
            return False
        
        infos = self.app.pluginStore.infoSaver.loadInfos()
        for pluginUrl in infos["installed-plugins"]:
            if infos["installed-plugins"][pluginUrl]["verified-commit"] != self.getPluginForUrl(pluginUrl)["verified-commit"]:
                return True
        return False
    
    def installUpdates(self):
        # Update local cache
        self.reloadCache()

        # Install updates
        infos = self.app.pluginStore.infoSaver.loadInfos()
        for pluginUrl in infos["installed-plugins"]:
            if infos["installed-plugins"][pluginUrl]["verified-commit"] != self.getPluginForUrl(pluginUrl)["verified-commit"]:
                self.installPlugin(pluginUrl, self.getPluginForUrl(pluginUrl)["verified-commit"], install=True)

    def installPlugin(self, pluginUrl, verifiedCommit, install=False):
        self.githubHelper.cloneAtCommit(pluginUrl, verifiedCommit, install=install)

        # Update pluginInfos.json
        infos = self.app.pluginStore.infoSaver.loadInfos()
        if "installed-plugins" not in infos:
            infos["installed-plugins"] = {}
        if pluginUrl not in infos["installed-plugins"]:
            infos["installed-plugins"][pluginUrl] = {}
        infos["installed-plugins"][pluginUrl]["verified-commit"] = verifiedCommit
        self.app.pluginStore.infoSaver.saveInfos(infos)

        # Import plugin
        if install:
            # Get name of repository
            projectName = pluginUrl.split("/")[-1]
            # Note: the .py file has the same name as the repository
            sys.path.append(os.path.join("plugins", projectName))
            importlib.import_module(projectName)
        
        # Update action selector
        self.app.buildActionSelector()
        self.app.loadCategories()

        # Regenerate action index
        self.app.communicationHandler.loadActionIndex()
            
    def getPluginForUrl(self, url:str):
        for plugin in self.plugins:
            if plugin["url"] == url:
                return plugin

    def downloadCache(self):
        #TODO: Detect missing folders and reload them even if nothing has changed in Plugins.json
        oldPLuginList, newPluginList = self.getJsons()
        changedPlugins = self.getChangedPlugins()

        for plugin in changedPlugins:
            # Get backend infos
            if "url" not in newPluginList[plugin]: continue
            pluginUrl = newPluginList[plugin]["url"]

            if "verified-commit" not in newPluginList[plugin]: continue
            pluginVerifiedCommit = newPluginList[plugin]["verified-commit"]

            pluginName = pluginUrl.split("/")[-1]
            manDst = f"tmp/cache/{pluginName}/manifest.json"
            self.makeDirsToFile(manDst)
            manifest = self.downloadPluginManifest(pluginUrl, manDst, pluginVerifiedCommit)     
            copyToFolder = f"tmp/cache/{pluginName}/"
            manifest = json.loads(manifest)
            remotePath = manifest["thumbnail"]
            self.downloadPluginThumbnail(pluginUrl, copyToFolder, remotePath,pluginVerifiedCommit)  

            pluginDict = {
                "name": pluginName,
                "url": pluginUrl,
                "cache-path": copyToFolder,
                "verified-commit": pluginVerifiedCommit,
                "user": self.githubHelper.getUserNameFromUrl(pluginUrl),
                "manifestPath": manDst,
                "thumbnailPath": os.path.join(copyToFolder, os.path.split(remotePath)[1])
            }

            self.plugins.append(pluginDict)
            # Save file
            with open("plugins/PluginsCacheInfos.json", "w") as file:
                json.dump(self.plugins, file, indent=4)

        #TODO: Delete plugins that are not in the new list

        # Save new plugin list
        with open("plugins/Plugins.json", "w") as file:     
            json.dump(newPluginList, file, indent=4)

        self.ready = True

    def getJsons(self) -> tuple:
        newPluginList = self.githubHelper.getRaw("https://github.com/Core447/StreamController-Plugins-archive", "Plugins.json", branchName="main")
        if newPluginList == None:
            print("Plugin list could not be loaded")
            return
        newPluginList = json.loads(newPluginList)
        # Save the json
        # with open("tmp/Plugins.json.new", "w") as file:
            # json.dump(newPluginList, file, indent=4)
        # Open old json
        if os.path.exists("plugins/Plugins.json"):
            with open("plugins/Plugins.json", "r") as file:
                oldPluginList = json.load(file)
        else:
            oldPluginList = {}

        return oldPluginList, newPluginList
    
    def getChanges(self, oldPluginList, newPluginList) -> list:
        changedPlugins = []
        for plugin in newPluginList:
            if plugin not in oldPluginList:
                changedPlugins.append(plugin)
                continue

            # Fix missing keys
            if "url" not in oldPluginList[plugin]:
                oldPluginList[plugin]["url"] == None
            if "url" not in newPluginList[plugin]:
                newPluginList[plugin]["url"] == None
            if "verified-commit" not in oldPluginList[plugin]:
                oldPluginList[plugin]["verified-commit"] == None
            if "verified-commit" not in newPluginList[plugin]:
                newPluginList[plugin]["verified-commit"] == None

            if newPluginList[plugin]["url"] != oldPluginList[plugin]["url"]:
                changedPlugins.append(plugin)
                continue

            if newPluginList[plugin]["verified-commit"] != oldPluginList[plugin]["verified-commit"]:
                changedPlugins.append(plugin)
                continue

        return changedPlugins
    
    def downloadPluginManifest(self, pluginUrl: str, copyTo: str, sha: str):
        if pluginUrl == None: return
        if copyTo == None: return
        if sha == None: return

        repoName = pluginUrl.split("/")[-1]

        remotePath = "manifest.json"
        fileExtension = os.path.splitext(remotePath)[1]
        manifest = self.githubHelper.downloadFile(pluginUrl, remotePath, copyTo, commitSHA=sha, returnFile=True)
        if manifest is False:
            return None
        return manifest

    def downloadPluginThumbnail(self, pluginUrl: str, copyToFolder: str, remotePath: str, sha: str):
        if pluginUrl == None: return
        if copyToFolder == None: return
        if sha == None: return

        repoName = pluginUrl.split("/")[-1]

        success = self.githubHelper.downloadFile(pluginUrl, remotePath, os.path.join(copyToFolder, os.path.split(remotePath)[1]), commitSHA=sha)
        if not success:
            return None
        return True

    def makeDirsToFile(self, path:str):
        folderPath = os.path.dirname(path)
        os.makedirs(folderPath, exist_ok=True)

if __name__ == "__main__":
    thread = StoreLoadingThread(None)
    thread.start()