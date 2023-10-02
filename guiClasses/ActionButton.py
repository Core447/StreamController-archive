from gi.repository import Gtk, Gdk
from guiClasses.ConfigButton import ConfigButton
class ActionButton(ConfigButton):
    def __init__(self, app, label, iconPath, eventTag: str):
        #TODO: check if eventTag is already in use
        #check eventTag
        self.app = app
        if not isinstance(eventTag, str):
            raise TypeError("eventTag must be a String")
        if len(eventTag) == 0:
            return
        self.eventTag = eventTag
        super().__init__(label)
        self.buttonIcon.set_from_file(iconPath)

        self.createDnD()

    def createDnD(self):
        #Create all elements needed for drag and drop      
        dnd = Gtk.DragSource()
        dnd.set_actions(Gdk.DragAction.COPY)
        dnd.connect('prepare', self.on_dnd_prepare)
        dnd.connect('drag-begin', self.on_dnd_begin)
        dnd.connect('drag-end', self.on_dnd_end)
        self.buttonGrid.add_controller(dnd)

    def on_dnd_prepare(self, drag_source, x, y):      
        drag_source.set_icon(
            Gtk.WidgetPaintable.new(self),
            self.get_width() / 2, self.get_height() / 2
        )

        content = Gdk.ContentProvider.new_for_value(self)
        return content

    def on_dnd_begin(self, drag_source, data):
        content = data.get_content()

        #config preview in multiaction config button
        if self.app.leftStack.get_visible_child_name() == "multi":
            self.app.MultiActionConfig.preview.set_label("".join(self.eventTag.split(":")[1:]))

    def on_dnd_end(self, drag, drag_data, flag):
        pass