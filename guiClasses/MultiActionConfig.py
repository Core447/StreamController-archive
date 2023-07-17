from gi.repository import Gtk, Gdk
class MultiActionConfig(Gtk.Box):
    def __init__(self, app) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.app = app
        self.actionBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, hexpand=True, vexpand=True, homogeneous=True)
        self.actionBox.add_css_class("linked")

        #add info grid
        self.infoGrid = Gtk.Grid(margin_start=5, margin_bottom=5, margin_top=5)
        self.append(self.infoGrid)

        #add back button
        self.backButton = Gtk.Button(icon_name="go-previous")
        self.backButton.connect("clicked", self.onBack)
        self.infoGrid.attach(self.backButton, 0, 0, 1, 1)

        #add title
        self.title = Gtk.Label(label="Multi Action Config", css_classes=["multi-action-config-title"])
        self.infoGrid.attach(self.title, 1, 0, 1, 1)

        #add seperator
        self.append(Gtk.Separator())

        
        #add actionBox
        self.append(self.actionBox)

    def addActionButton(self, action):
        label = self.app.communicationHandler.actionIndex[action].ACTION_NAME
        self.actionBox.append(Gtk.Button(label=label, height_request=75, width_request=500))

    def loadFromActions(self, actions: list):
        #check if there are any actions
        if actions == None: return

        self.clearAllLoadedButtons()
        for action in actions:
            self.addActionButton(action)

        self.app.leftStack.set_visible_child(self)

    def clearAllLoadedButtons(self):
        while self.actionBox.get_first_child() != None:
            self.actionBox.remove(self.get_first_child())

    def onBack(self, widget):
        self.app.leftStack.set_visible_child_name("main")