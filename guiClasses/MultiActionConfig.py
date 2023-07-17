from gi.repository import Gtk, Gdk
class MultiActionConfig(Gtk.Box):
    def __init__(self, app) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        self.app = app
        self.loadTestGrid()
        self.add_css_class("linked")

        self.app.leftStack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
    
    def loadTestGrid(self):
        for i in range(0, 5):
            self.append(Gtk.Button(label=f"Button: {i}", height_request=75, width_request=500))   

    def addActionButton(self, action):
        label = self.app.communicationHandler.actionIndex[action].ACTION_NAME
        self.append(Gtk.Button(label=label, height_request=75, width_request=500))


    def loadFromActions(self, actions: list):
        #check if there are any actions
        if actions == None: return

        self.clearAllLoadedButtons()
        for action in actions:
            self.addActionButton(action)

        self.app.leftStack.set_visible_child(self)

    def clearAllLoadedButtons(self):
        while self.get_first_child() != None:
            self.remove(self.get_first_child())