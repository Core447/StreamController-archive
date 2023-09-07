from gi.repository import Gtk, Gdk, Adw, Gio, GLib
from guiClasses.ConfigButton import ConfigButton

class PageManager(Gtk.ApplicationWindow):
    # This variable is used to inform the PageManager to which page the actions belong
    nameOfSelectedPage = None

    def __init__(self, app):
        self.app = app
        super().__init__(title="Page Manager")
        self.set_default_size(400, 550)
        # self.set_position(Gtk.WindowPosition.CENTER)
        # self.show()
        # self.do_grab_focus()
        self.build()
    
    def showWindow(self):
        self.show()
        # self.grab_focus()
        self.set_transient_for(self.app.win)
        # self.set_modal(False)
        # self.app.win.set_modal(False)


    def build(self):
        # Title bar
        self.titleBar = Gtk.HeaderBar()
        self.set_titlebar(self.titleBar)

        # Box for the buttons
        self.buttonBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,valign=Gtk.Align.CENTER, hexpand=True, vexpand=True, homogeneous=True, css_classes=['linked'])
        self.set_child(self.buttonBox)

        # Add the buttons
        self.loadPages()

        # Init the actions
        self.initActions()

    def loadPages(self):
        self.clearButtonBox()
        for pageName in self.app.communicationHandler.createPagesList(onlyName = True):
            self.buttonBox.append(PageManagerButton(self, pageName))
        
    def clearButtonBox(self):
        while self.buttonBox.get_first_child() is not None:
            self.buttonBox.remove(self.buttonBox.get_first_child())
        
    def initActions(self):
        # Create actions
        self.removeAction = Gio.SimpleAction.new("remove", None)

        # Connect actions
        self.removeAction.connect("activate", self.removePage)

        # Add actions
        self.add_action(self.removeAction)

    # Hamburger Menu actions
    def removePage(self, action, param):
        if PageManager.nameOfSelectedPage is None:
            return
        print(f"remove {PageManager.nameOfSelectedPage}")
        self.app.communicationHandler.deletePage(PageManager.nameOfSelectedPage)
        self.app.pageSelector.update()
        self.loadPages()
        

class PageManagerButton(Gtk.Grid):
    def __init__(self, pageManager: PageManager, pageName):
        super().__init__(height_request=75, hexpand=True, vexpand=True, margin_start=20, margin_end=20, css_classes=['linked'])
        self.pageManager = pageManager
        self.pageName = pageName
        self.build()

    def build(self):
        self.label = Gtk.Label(label=self.pageName)
        self.button = Gtk.Button(hexpand=True, vexpand=True)
        self.button.set_child(self.label)
        self.menu = PageManagerHamburgerMenuButton(pageName = self.pageName)

        self.attach(self.button, 0, 0, 1, 1)
        self.attach(self.menu, 1, 0, 1, 1)

        self.button.connect('clicked', self.onClick)

    def onClick(self, button):
        # Change page
        self.pageManager.app.communicationHandler.deckController[0].loadPage(self.pageName, True)

        # Update active page in PageSelector in main window
        self.pageManager.app.pageSelector.update()
    

class PageManagerHamburgerPopup(Gtk.PopoverMenu):
    def __init__(self):
        super().__init__()

        # Create the menu 
        self.menu = Gio.Menu.new()

        # Add the menu items
        self.menu.append("Remove", "win.remove")

        self.set_menu_model(self.menu)
        

class PageManagerHamburgerMenuButton(Gtk.Button):
    def __init__(self, pageName):
        self.pageName = pageName
        super().__init__(vexpand=True, icon_name="open-menu-symbolic")

        # Create the popover
        self.popover = PageManagerHamburgerPopup()
        self.popover.set_parent(self)

        self.connect('clicked', self.onClick)

    def onClick(self, button):
        print("Clicked Page Manager")
        self.popover.popup()
        PageManager.nameOfSelectedPage = self.pageName