from gi.repository import Gtk, Gdk, Gio
from guiClasses.ConfigButton import ConfigButton
class GridButton(Gtk.Button):
    def __init__(self, grid: Gtk.Grid, row: int, column: int):
        super().__init__()
        self.set_css_classes(["gridButton"])

        grid.attach(self, column, row, 1, 1) 

        #Drag and drop
        #button.connect('drag_begin', self.dragBegin )

        #button.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        #button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)

        
        dnd = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        dnd.connect('drop', self.on_dnd_drop)
        dnd.connect('accept', self.on_dnd_accept)
        dnd.connect('enter', self.on_dnd_enter)
        dnd.connect('motion', self.on_dnd_motion)
        dnd.connect('leave', self.on_dnd_leave)
        self.add_controller(dnd)      
        
        self.image = Gtk.Image(hexpand=True, vexpand=True)
        self.set_child(self.image)

    
    def on_dnd_drop(self, drop_target, value, x, y):
        print(f'in on_dnd_drop(); value={value}, x={x}, y={y}')
        print(list(value))

    def on_dnd_accept(self, drop, user_data):
        print(f'in on_dnd_accept(); drop={drop}, user_data={user_data}')
        return True

    def on_dnd_enter(self, drop_target, x, y):
        print(f'in on_dnd_enter(); drop_target={drop_target}, x={x}, y={y}')
        return Gdk.DragAction.COPY

    def on_dnd_motion(self, drop_target, x, y):
        print(f'in on_dnd_motion(); drop_target={drop_target}, x={x}, y={y}')
        return Gdk.DragAction.COPY

    def on_dnd_leave(self, user_data):
        print(f'in on_dnd_leave(); user_data={user_data}')