from gi.repository import Gtk, Gdk, Adw, Gio, GLib, GdkPixbuf, Gsk, Pango
import sys, webbrowser, os, shutil

# Import own modules
sys.path.append("guiClasses/PluginStore")
from OfficialMark import OfficialMark

class PluginPreview(Gtk.FlowBoxChild):
    def __init__(self, pluginStore, pluginName, pluginDescription, thumbnailPath, userName, stargazers, websiteUrl, verifiedCommit, official):
        self.pluginStore = pluginStore
        self.pluginName = pluginName
        self.pluginDescription = pluginDescription
        self.thumbnailPath = thumbnailPath
        self.userName = userName
        self.stargazers = stargazers
        self.websiteUrl = websiteUrl 
        self.verifiedCommit = verifiedCommit
        self.official = official

        super().__init__(width_request=100, height_request=100)
        self.set_name(pluginName)
        self.build()
        
    def build(self):
        self.mainBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=False,
            css_classes=["no-bottom-rounding"]
        )
        self.set_child(self.mainBox)

        self.mainButton = Gtk.Button(
            hexpand=True,
            vexpand=False,
            width_request=250,
            height_request=200,
            margin_start=0,
            margin_end=0,
            css_classes=["no-padding", "no-bottom-rounding"]
        )
        self.mainBox.append(self.mainButton)

        self.mainButtonBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=False,
            homogeneous=False
        )
        self.mainButton.set_child(self.mainButtonBox)

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            self.thumbnailPath,
            width=250,
            height=90,
            preserve_aspect_ratio=False
        )
        self.image = Gtk.Picture(
            hexpand=False,
            css_classes=["plugin-store-image"],
            content_fit=Gtk.ContentFit.COVER,
            height_request=90,
            width_request=250,
            vexpand_set=True
        )
        self.image.set_pixbuf(self.pixbuf)
        self.image.set_valign(Gtk.Align.START)
        if self.thumbnailPath is None:
            self.mainButtonBox.append(Gtk.Label(label="No image provided",
                                                halign=Gtk.Align.CENTER,
                                                width_request=250,
                                                height_request=90,
                                                css_classes=["plugin-store-no-thumbnail"]))
        else:
            self.mainButtonBox.append(self.image)

        self.bottomBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=False,
            valign=0,
            margin_start=5,
            margin_top=5
        )
        self.mainButtonBox.append(self.bottomBox)

        self.nameLabel = Gtk.Label(
            label=self.pluginName,
            halign=Gtk.Align.START,
            css_classes=["plugin-store-name"]
        )
        self.bottomBox.append(self.nameLabel)

        self.marksBox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.START,
            hexpand=True,
            margin_top=5
        )
        self.bottomBox.append(self.marksBox)

        self.marksBox.append(OfficialMark())

        self.userNameLabel = Gtk.Label(
            label=f"By {self.userName}",
            halign=Gtk.Align.START,
            sensitive=False,
            margin_start=2,
            margin_top=7
        )
        self.bottomBox.append(self.userNameLabel)

        self.stargazersLabel = Gtk.Label(
            label=f"{self.stargazers} GitHub Stars",
            halign=Gtk.Align.START,
            sensitive=False,
            margin_start=2,
            margin_top=2
        )
        if self.stargazers is not None:
            self.bottomBox.append(self.stargazersLabel)

        self.descriptionLabel = Gtk.Label(
            label=self.pluginDescription,
            halign=Gtk.Align.START,
            css_classes=["plugin-store-description"],
            margin_top=7,
            wrap=True,
            lines=5,
            max_width_chars=20,
            ellipsize=Pango.EllipsizeMode.END,
            margin_bottom=10
        )
        if self.pluginDescription is not None:
            self.bottomBox.append(self.descriptionLabel)

        self.mainButtonBox.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True))

        self.buttonBox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.FILL,
            hexpand=True,
            margin_top=0,
            homogeneous=True,
            css_classes=["linked"]
        )
        self.mainBox.append(self.buttonBox)

        self.downloadButton = Gtk.Button(
            icon_name="download-symbolic",
            # width_request=50,
            hexpand=True,
            css_classes=["no-top-rounding", "no-bottom-right-rounding"]
        )
        self.downloadButton.connect("clicked", self.onClickDownload)
        self.buttonBox.append(self.downloadButton)

        self.websiteButton = Gtk.Button(
            icon_name="github-symbolic",
            hexpand=True,
            css_classes=["no-top-rounding", "no-bottom-left-rounding"]
        )
        self.websiteButton.connect("clicked", self.onClickWebsite)
        self.buttonBox.append(self.websiteButton)

        # Update download button icon status
        self.setInstallButtonIconStatus()


    def onClickDownload(self, widget):
        print(self.downloadButton.get_icon_name())
        if self.downloadButton.get_icon_name() == "edit-delete":
            # Remove the plugin
            self.unInstall()        
        else:
            # Install or update the plugin
            self.install()

        # Update download button
        self.setInstallButtonIconStatus()

    def unInstall(self):
        pluginPath = os.path.join("plugins", self.pluginName)
        # Remove everthing inside the folder except buttonSettings.json
        self.pluginStore.githubHelper.clearDirExceptSettings(pluginPath)

        # Update pluginInfos.json
        infos = self.pluginStore.infoSaver.loadInfos()
        del infos["installed-plugins"][self.websiteUrl]
        self.pluginStore.infoSaver.saveInfos(infos)

    def install(self):
        self.pluginStore.githubHelper.cloneAtCommit(self.websiteUrl, self.verifiedCommit, install=True)

        # Update pluginInfos.json
        infos = self.pluginStore.infoSaver.loadInfos()
        if "installed-plugins" not in infos:
            infos["installed-plugins"] = {}
        if self.websiteUrl not in infos["installed-plugins"]:
            infos["installed-plugins"][self.websiteUrl] = {}
        infos["installed-plugins"][self.websiteUrl]["verified-commit"] = self.verifiedCommit
        self.pluginStore.infoSaver.saveInfos(infos)

    def onClickWebsite(self, widget):
        webbrowser.open_new_tab(self.websiteUrl)

    # Helper methods
    def isInstalled(self):
        infos = self.pluginStore.infoSaver.loadInfos()
        if "installed-plugins" not in infos:
            return False
        if self.websiteUrl not in infos["installed-plugins"]:
            return False
        return True
    
    def isUpToDate(self):
        if not self.isInstalled():
            return False
        infos = self.pluginStore.infoSaver.loadInfos()
        # No need to verify the infos, because self.isInstalled already did
        
        return infos["installed-plugins"][self.websiteUrl]["verified-commit"] == self.verifiedCommit
    
    def setInstallButtonIconStatus(self):
        if self.isInstalled():
            self.downloadButton.set_icon_name("edit-delete")
        else:
            self.downloadButton.set_icon_name("download-symbolic")
            return
        if not self.isUpToDate():
            self.downloadButton.set_icon_name("software-update-available")
        