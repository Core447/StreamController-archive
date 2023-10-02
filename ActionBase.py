class ActionBase():
    #List of all instances
    instances = []
    actions = {}

    #Change these variables to match your action
    ACTION_NAME = ""
    def __init__(self):
        ActionBase.instances.append(self)
        if self.ACTION_NAME in ActionBase.actions:
            raise ValueError(f"Action {self.ACTION_NAME} already exists") # TODO: Raise only if the other action is from the same plugin
        ActionBase.actions[self.ACTION_NAME] = self
        pass

    def onKeyDown(self, deck, keyIndex):
        pass

    def onKeyUp(self, deck, keyIndex):
        pass

    def onTick(self, deck):
        pass