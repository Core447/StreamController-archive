from gi.repository import Gtk
from guiClasses.ConfigButton import ConfigButton
class CategoryButton(ConfigButton):
    def __init__(self, grid, stack: Gtk.Stack, row, label):
        self.label = label
        self.stack = stack
        super().__init__(label)
        self.buttonIcon.set_from_icon_name("stock_open")

        grid.attach(self, 0, row, 1, 1)
        self.connect("clicked", self.onClick)

    def onClick(self, button):
        self.stack.set_visible_child_name(self.label)