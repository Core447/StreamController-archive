from gi.repository import Gtk, Gdk
from guiClasses.ConfigButton import ConfigButton
class ActionButton(ConfigButton):
    def __init__(self, grid, row, label, iconPath):
        super().__init__(label)
        self.buttonIcon.set_from_file(iconPath)

        self.createDnD()
        grid.attach(self, 0, row, 1, 1)

    def createDnD(self):
        #Create all elements needed for drag and drop      
        dnd = Gtk.DragSource()
        dnd.set_actions(Gdk.DragAction.COPY)
        dnd.connect('prepare', self.on_dnd_prepare)
        dnd.connect('drag-begin', self.on_dnd_begin)
        dnd.connect('drag-end', self.on_dnd_end)
        self.buttonGrid.add_controller(dnd)

    def on_dnd_prepare(self, drag_source, x, y):
        print(f'in on_dnd_prepare(); drag_source={drag_source}, x={x}, y={y}')
       
        drag_source.set_icon(
            Gtk.WidgetPaintable.new(self),
            self.get_width() / 2, self.get_height() / 2
        )

        content = Gdk.ContentProvider.new_for_value(self)
        return content

    def on_dnd_begin(self, drag_source, data):
        content = data.get_content()
        print(f'in on_dnd_begin(); drag_source={drag_source}, data={data}, content={content}')

    def on_dnd_end(self, drag, drag_data, flag):
        print(f'in on_dnd_end(); drag={drag}, drag_data={drag_data}, flag={flag}')