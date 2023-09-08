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

        #Main box
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.set_child(self.mainBox)

        # Box for the buttons
        self.buttonBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,valign=Gtk.Align.CENTER, hexpand=True, vexpand=True, css_classes=['linked'])
        self.mainBox.append(self.buttonBox)

        # Add the buttons
        self.loadPages()

        # Init the actions
        self.initActions()

        # Add a new box to the bottom of the window
        self.bottomBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, hexpand=True)

        # Add separator
        self.mainBox.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True))

        # Add 'Add New Page' button
        self.button = Gtk.Button(hexpand=True, label='Add New Page', margin_bottom=10, margin_top=10)
        self.button.connect("clicked", self.onClickCreateNewPage)
        self.bottomBox.append(self.button)
        self.mainBox.append(self.bottomBox)

    def loadPages(self):
        self.clearButtonBox()
        for pageName in self.app.communicationHandler.createPagesList(onlyName = True):
            self.buttonBox.append(PageManagerButton(self, pageName))
        
    def clearButtonBox(self):
        while self.buttonBox.get_first_child() is not None:
            self.buttonBox.remove(self.buttonBox.get_first_child())
        
    def initActions(self):
        # Create actions
        self.renameAction = Gio.SimpleAction.new("rename", None)
        self.removeAction = Gio.SimpleAction.new("remove", None)

        # Connect actions
        self.renameAction.connect("activate", self.renamePage)
        self.removeAction.connect("activate", self.showConfirmationDialog)

        # Add actions
        self.add_action(self.renameAction)
        self.add_action(self.removeAction)

    # Hamburger Menu actions
    def removePage(self):
        print('removing.....')
        if PageManager.nameOfSelectedPage is None:
            return
        print(f"remove {PageManager.nameOfSelectedPage}")
        self.app.communicationHandler.deletePage(PageManager.nameOfSelectedPage)
        self.loadPages()

    def showConfirmationDialog(self, action, params):
        dialog = ConfirmationDialog(self.app.win, self)
        dialog.show()

    def onClickCreateNewPage(self, button):
        print('create new page')
        pageDialog = CreatePageDialog(pageManager = self)
        pageDialog.show()

    def renamePage(self, action, params):
        if PageManager.nameOfSelectedPage is None:
            return
        pageDialog = RenamePageDialog(pageManager= self)
        pageDialog.show()
        

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

class PageManagerHamburgerPopup(Gtk.PopoverMenu):
    def __init__(self):
        super().__init__()

        # Create the menu 
        self.menu = Gio.Menu.new()

        # Add the menu items
        self.menu.append("Rename", "win.rename")
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

class ConfirmationDialog(Gtk.MessageDialog):
    def __init__(self, parent, pageManager: PageManager):
        self.pageManager = pageManager
        super().__init__(parent=parent, transient_for=parent, modal=True, buttons=Gtk.ButtonsType.OK_CANCEL, message_type=Gtk.MessageType.QUESTION, text=f"Are you sure you want to remove: {PageManager.nameOfSelectedPage}?")
        # Call function saved in callOnConfirm
        self.connect("response", self.onResponse)

    def onResponse(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            print('pressed OK')
            self.pageManager.removePage()
        self.destroy()

class NamePage(Gtk.ApplicationWindow):
    def __init__(self, pageManager: PageManager, title, defaultText:str = None, alwaysAllowPage:str = None, okButtonLabel:str = "OK"):
        self.pageManager = pageManager
        self.defaultText = defaultText
        self.alwaysAllowPage = alwaysAllowPage
        self.okButtonLabel = okButtonLabel
        super().__init__(transient_for=self.pageManager.app.win, modal=True, default_height=150, default_width=350, title = title)
        self.build()

    def build(self):
        # Create title bar
        self.titleBar = Gtk.HeaderBar(show_title_buttons=False)
        # Cancel button
        self.cancelButton = Gtk.Button(label='Cancel')
        self.cancelButton.connect('clicked', self.onCancel)
        # Confirm button
        self.confirmButton = Gtk.Button(label=self.okButtonLabel, css_classes=['confirm-button'], sensitive=False)
        self.confirmButton.connect('clicked', self.onConfirm)
        # Main box
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True, margin_start=20, margin_end=20, margin_top=20, margin_bottom=20)
        # Label
        self.label = Gtk.Label(label='Page Name:')
        # Input box
        self.inputBox = Gtk.Entry(hexpand=True, margin_top=10, text=self.defaultText)
        self.inputBox.connect('changed', self.onNameChange)
        # Warning label
        self.warningLabel = Gtk.Label(label="The name can't be empty", css_classes=['warning-label'], margin_top=10)

        # Add objects
        self.set_titlebar(self.titleBar)
        self.titleBar.pack_start(self.cancelButton)
        self.titleBar.pack_end(self.confirmButton)
        self.set_child(self.mainBox)
        self.mainBox.append(self.label)
        self.mainBox.append(self.inputBox)
        self.mainBox.append(self.warningLabel)

        # Set status
        self.onNameChange(self.inputBox)

    def onCancel(self, button):
        self.destroy()
    
    def onConfirm(self, button):
        return
        self.pageManager.app.communicationHandler.createNewPage(self.inputBox.get_text())
        self.pageManager.loadPages()
        self.destroy()

    def onNameChange(self, entry):
        if entry.get_text() == '':
            self.setDialogStatus(0)
        elif entry.get_text() not in self.pageManager.app.communicationHandler.createPagesList(onlyName = True) or entry.get_text() == self.alwaysAllowPage:
            self.setDialogStatus(2)
        else:
            self.setDialogStatus(1)

    def setDialogStatus(self, status):
        """
        Sets the status of the dialog

        Args:
            status (int): The status of the dialog: 0: no name; 1:already in use; 2:ok
        """
        if status == 0:
            # Label
            if self.mainBox.get_last_child() is not self.warningLabel:
                self.mainBox.append(self.warningLabel)
            self.warningLabel.set_text("The name can't be empty")
            # Button
            self.confirmButton.set_sensitive(False)
            self.confirmButton.set_css_classes(['confirm-button'])
        if status == 1:
            # Label
            if self.mainBox.get_last_child() is not self.warningLabel:
                self.mainBox.append(self.warningLabel)
            self.warningLabel.set_text("This name is already in use")
            # Button
            self.confirmButton.set_sensitive(False)
            self.confirmButton.set_css_classes(['confirm-button-error'])
        if status == 2:
            # Label
            if self.mainBox.get_last_child() is self.warningLabel:
                self.mainBox.remove(self.warningLabel)
            # Button
            self.confirmButton.set_sensitive(True)
            self.confirmButton.set_css_classes(['confirm-button'])


class CreatePageDialog(NamePage):
    def __init__(self, pageManager: PageManager):
        super().__init__(pageManager, "Create New Page", okButtonLabel="Create")

    def onConfirm(self, button):
        self.pageManager.app.communicationHandler.createNewPage(self.inputBox.get_text())
        self.pageManager.loadPages()
        super().destroy()


class RenamePageDialog(NamePage):
    def __init__(self, pageManager: PageManager):
        super().__init__(pageManager, "Rename Page", alwaysAllowPage = PageManager.nameOfSelectedPage, defaultText=PageManager.nameOfSelectedPage, okButtonLabel="Rename")

    def onConfirm(self, button):
        self.pageManager.app.communicationHandler.renamePage(PageManager.nameOfSelectedPage, self.inputBox.get_text())
        self.pageManager.loadPages()
        super().destroy()