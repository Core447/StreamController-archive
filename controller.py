#imports
import StreamDeck
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
import StreamDeck.Devices
import os
import json
from PIL import Image, ImageDraw, ImageFont
import importlib
import threading
from time import sleep

from gi.repository import Gtk, Adw, Gdk


# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
from PluginBase import PluginBase








class CommunicationHandler():
    def __init__(self):
        self.actionIndex = {}
        self.app = None
        self.deckController = []
        self.startTickHandler()
        return
    
    def initDecks(self):
        decks = DeviceManager().enumerate()
        for index, deck in enumerate(decks):
            deckController = DeckController(deck, self)
            self.deckController.append(deckController)
            deckController.loadPage("main")
    
    def closeDecks(self, reset:bool = False):
        decks = DeviceManager().enumerate()
        for deck in decks:
            try:
                deck.open()
                if reset: deck.reset()
            except:
                pass

            try:
                deck.close()
            except:
                pass

    def loadActionIndex(self):
        self.actionIndex = {}
        for key in list(PluginBase.plugins.keys()):
            for action in PluginBase.plugins[key].pluginActions:
                print(f"action: {action.ACTION_NAME} from plugin: {key}")
                if (key + ":" + action.ACTION_NAME) in list(self.actionIndex.keys()):
                    raise ValueError(f"Duplicate action {action.ACTION_NAME} in plugin {key}")
                self.actionIndex[key + ":" + action.ACTION_NAME] = action

    def loadPlugins(self):
        #Load all plugins
        path = "plugins"

        for folder in os.listdir(path):
            if not os.path.isdir(os.path.join(path, folder)):
                continue
            if os.path.exists(os.path.join(path, folder, folder+".py")):
                modulePath = path.replace("/",".") + "." + folder + "." + folder
                if modulePath[0] == ".": modulePath = modulePath[1:]
                print(modulePath)
                importlib.import_module(modulePath)

    #helper methods
    def getCurrentPageName(self) -> str:
        return self.app.pageSelector.comboBox.get_child().get_text()
        

    def getCurrentPageJson(self):
        pageName = self.getCurrentPageName()
        #check if page exists
        pageFilePath = os.path.join("pages", pageName + ".json")
        if not os.path.exists(pageFilePath):
            raise FileNotFoundError(f"Page {pageName} does not exist")

        with open(pageFilePath) as file:
            pageData = json.load(file)
        
        return pageData
    
    def startTickHandler(self):
        tickThread = threading.Thread(target=self.handleTickMethods)
        tickThread.start()
    
    def handleTickMethods(self):
        while True:
            for deckController in self.deckController:
                deckController.handleTickMethods()
            sleep(1)


    

class DeckController():
    def __init__(self, deck: StreamDeck.Devices, communicationHandler: CommunicationHandler):
        #check if deck is a StreamDeck.Devices object
        #TODO: Enable this
        #if not issubclass(type(deck), StreamDeck.Devices):
        #    raise ValueError("Deck must be a StreamDeck.Devices object")
        #    return
        self.communicationHandler = communicationHandler
        self.deck = deck
        self.deck.open()
        self.loadedPage = None
        self.loadedPageJson = None
        self.loadedButtons = {} #a dict that keeps track of loaded buttons to avoid reloading them when not needed

        #Register callback function (handles key presses)
        deck.set_key_callback(self.keyChangeCallback)

    def reset(self):
        self.deck.reset()
        


        #Wait until keyGrid is loaded
        hadToWaitForKeyGrid = False
        while not hasattr(self.communicationHandler.app, "keyGrid"):
            hadToWaitForKeyGrid = True
            pass #wait until keyGrid is loaded
        if hadToWaitForKeyGrid:
            sleep(0.25) #wait for keyGrid to load all keys
        for button in self.communicationHandler.app.keyGrid.gridButtons:
            #button.image = Gtk.Image(hexpand=True, vexpand=True)
            button.image.clear()
            continue


    #functions
    def loadPage(self, pageName: str, update: bool = False):
        """
        Load a page by its name.

        Args:
            pageName (str): The name of the page to load.

        Raises:
            ValueError: If `pageName` is not a string.
            FileNotFoundError: If the page file does not exist.

        Returns:
            None
        """
        #check if name is a string
        print(f"** loading Page: {pageName}")
        if not isinstance(pageName, str):
            raise ValueError("Page name must be a string")
        
        #check if page is already loaded
        if self.loadedPage == pageName and not update:
            return
        
        #check if page exists
        pageFilePath = os.path.join("pages", pageName + ".json") #Load the corresponding page file
        if not os.path.exists(pageFilePath):
            raise FileNotFoundError(f"Page {pageName} does not exist")
        
        #load page
        #TODO: only reload and clear buttons that changed
        self.reset() #Reset the deck
        with open(pageFilePath) as file:
            pageData = json.load(file)

        buttons = pageData["buttons"]
        for button in buttons.items():
            buttonIndex = self.buttonNameToIndex(button[0])
            self.loadButton(buttonIndex, buttons[button[0]]["default-image"], buttons[button[0]]["captions"], "Roboto-Regular.ttf", update=update)

        #set loadedPage variables
        self.loadedPage = pageName
        self.loadedPageJson = pageData

    def loadButton(self, keyIndex: int, imageName: str, captions: list, fontName: str, update: bool = False):
        if keyIndex in self.loadedButtons and not update:
            if self.loadedButtons[keyIndex] == [imageName, captions, fontName]:
                #exact same button is already loaded, skipping...
                return

        #check if keyIndex is an int
        if not isinstance(keyIndex, int):
            raise ValueError("Key index must be an int")
        #check if imagePath is a string
        if not isinstance(imageName, str):
            raise ValueError("Image path must be a string")
        #check if captions is a list
        if not isinstance(captions, list):
            raise ValueError("Captions must be a list")
        #check if font is a string
        if not isinstance(fontName, str):
            raise ValueError("Font must be a string")
        
        
                    
        #load the button
        #image = self.createDeckImage(imageName, captions, fontName)
        deckImage, uiImage = self.createDeckImages(imageName, captions, fontName)
        self.deck.set_key_image(keyIndex, deckImage)


        
        #Wait until keyGrid is loaded
        hadToWaitForKeyGrid = False
        while not hasattr(self.communicationHandler.app, "keyGrid"):
            hadToWaitForKeyGrid = True
            pass #wait until keyGrid is loaded
        if hadToWaitForKeyGrid:
            sleep(0.25) #wait for keyGrid to load all keys


        uiImage.save(os.path.join("tmp", "lastLoadedIcon.png"))
        #TODO: Find solution to avoid saving image
        self.communicationHandler.app.keyGrid.gridButtons[keyIndex].image.set_from_file(os.path.join("tmp", "lastLoadedIcon.png"))

        self.loadedButtons[keyIndex] = [imageName, captions, fontName]

    
    #helper functions
    def getJsonKeySyntaxByIndex(self, keyIndex):
        row = keyIndex // self.deck.key_layout()[1]
        column = keyIndex % self.deck.key_layout()[1]

        return f"{row}x{column}"
    
    def createDeckImages(self, iconFilename: str, captions: list = [], fontName: str = "Roboto-Regular.ttf"):
        """
        Generate the deck images with captions and icons.

        Parameters:
            iconFilename (str): The filename of the icon image, empty string for black background.
            captions (list, optional): The list of captions to be added to the images. Defaults to an empty list.
            fontName (str, optional): The filename or path of the font. Defaults to "Roboto-Regular.ttf".

        Returns:
            tuple: A tuple containing the deck image and the UI image.
        """

        #Create deck image
        #check if iconFilename is a string
        if not isinstance(iconFilename, str):
            raise ValueError("Icon filename must be a string")
        #check if captions is a list
        if not isinstance(captions, list):
            print(captions)
            raise ValueError("Captions must be a list")
        #check if fontFilename is a string
        if not isinstance(fontName, str):
            raise ValueError("Font filename must be a string")
        
        #check if font exists and search it
        if "/" in fontName:
            #a full path to the font was given, we can skip the search
            fontPath = os.path(fontName)
        else:
            #no exact path was given, we need to search the font in the most common paths
            fontPath = fontName
            if not os.path.exists(fontPath):
                fontPath = os.path.join(ASSETS_PATH, "fonts", fontName)
                if not os.path.exists(fontPath):
                    fontPath = os.path(os.path.join("/usr/share/fonts", fontName))
                    if not os.path.exists(fontPath):
                        raise FileNotFoundError(f"Font {fontName} could not be found")
                    
        #create icon
        if iconFilename == "":
            deckIcon = Image.new("RGB", (32, 32), (0,0,0))
            uiIcon = Image.new("RGBA", (32, 32), (0,0,0,0))
        else:
            imagePath = os.path.join(ASSETS_PATH, "images", iconFilename) if "/" not in iconFilename else iconFilename
            deckIcon = Image.open(imagePath)
            uiIcon = Image.open(imagePath)
        deckImage = PILHelper.create_scaled_image(self.deck, deckIcon, margins=[0, 0, 0, 0], background=((0,0,0)))
        uiImage = Image.new("RGBA", deckImage.size, (0,0,0,0))
       
        #create a draw object
        deckDraw = ImageDraw.Draw(deckImage)
        uiDraw = ImageDraw.Draw(uiImage)

        #scale uiIcon
        thumbnail_max_width = deckImage.width
        thumbnail_max_height = deckImage.height

        thumbnail = uiIcon
        uiIcon = uiIcon.thumbnail((thumbnail_max_width, thumbnail_max_height), Image.LANCZOS)

        thumbnail_x = ((thumbnail_max_width - thumbnail.width) // 2)
        thumbnail_y = ((thumbnail_max_height - thumbnail.height) // 2)

        #uiImage = uiImage.convert("RGBA")
        thumbnail = thumbnail.convert("RGBA")

        uiImage.paste(thumbnail, (thumbnail_x, thumbnail_y), thumbnail)
        
        #Add icon to uiImage
        #uiIcon = uiIcon.resize((50,50))
        #uiImage.paste(uiIcon, (0, 0))


        #load json from string
        captions = str(captions).replace("'",'"')
        captions = json.loads(captions)
        print(f"captions: {captions}")
        
        fontSize = 14
        for caption in captions:
            #Load font
            font = ImageFont.truetype(os.path.join(ASSETS_PATH, "fonts", fontPath), fontSize)
            #Draw captions on to the image
            deckDraw.text((deckImage.width / 2, deckImage.height*caption[0]["text-location"]+fontSize/2), text=caption[0]["text"], font=font, anchor="ms", fill="white")
            uiDraw.text((uiImage.width / 2, uiImage.height*caption[0]["text-location"]+fontSize/2), text=caption[0]["text"], font=font, anchor="ms", fill="white")
        
        deckImage.save(os.path.join("tmp", "lastLoadedIcon.png"))

        


        return PILHelper.to_native_format(self.deck, deckImage), uiImage
                    
    
    def buttonNameToIndex(self, buttonName: str):
        """
        Convert a button name (used in the config jsons) to its corresponding index on the StreamDeck.

        Parameters:
            buttonName (str): The name of the button.

        Returns:
            int: The index of the button on the StreamDeck.

        Raises:
            ValueError: If buttonName is not a string.
        """
        #check if buttonName is a string
        if not isinstance(buttonName, str):
            raise ValueError("Button name must be a string")

        buttonCoords = buttonName.split("x")
        buttonCoords[0] = int(buttonCoords[0])
        buttonCoords[1] = int(buttonCoords[1])
        
        #check if button is defined on the current StreamDeck
        if buttonCoords[0] > self.deck.key_layout()[0] or buttonCoords[1] > self.deck.key_layout()[1]:
            return None
        print(f"Button: {buttonName}, returned: {buttonCoords[0]*self.deck.key_layout()[1] + buttonCoords[1]}")
        return buttonCoords[0]*self.deck.key_layout()[1] + buttonCoords[1]
    
    def keyChangeCallback(self, deck, key, state):
        # Print new key state
        print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)
        print(f"KeyCoords: {self.getJsonKeySyntaxByIndex(key)}")
        button = self.loadedPageJson["buttons"]
        if button is None or self.getJsonKeySyntaxByIndex(key) not in button:
            #button is not defined
            return
        
        if state == True and button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-press"] != "none":
            print(button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-press"])
            self.doActions(button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-press"], key, True)
        elif state == False and button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-release"] != "none":
            print(button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-release"])
            self.doActions(button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-release"], key, False)


    def doActions(self, actions: list, keyIndex: int, keyState: bool):
        """
        Perform a series of actions based on the given list of actions.

        Parameters:
            actions (list): A list of actions to be performed.
            keyIndex: The index of the key.
            keyState (bool): The state of the key.

        Returns:
            None
        """
        #check if keyIndex is an int
        if not isinstance(keyIndex, int):
            raise ValueError(f"Key index must be an int. Got {keyIndex}")
        

        print("got:")
        print(actions)
        for action in actions:
            if action not in list(self.communicationHandler.actionIndex.keys()):
                print(f"Action '{action}' not found, skipping")
                continue
            if keyState == True:
                self.communicationHandler.actionIndex[action].onKeyDown(self, self.deck, keyIndex)
            else:
                self.communicationHandler.actionIndex[action].onKeyUp(self, self.deck, keyIndex)

    def handleTickMethods(self):
        if self.loadedPageJson == None:
            #no page loaded (yet)
            return
        print("tick....")

        pageData = self.loadedPageJson
        for buttonName in pageData["buttons"]:
            actionName = pageData["buttons"][buttonName]["actions"]["on-press"][0] #TODO: Find solution to show not only the first, maybe only allow one action and seperate multiactions completely
            if actionName == "none":
                print(f"buttonName: {buttonName}, no action defined")
                #no action defined
                continue
            action = self.communicationHandler.actionIndex[actionName]
            if hasattr(action, "tick"):
                print("object has tick method")

                controller = self
                deck = self.deck
                keyIndex = self.buttonNameToIndex(buttonName)
                print(f"updating index: {keyIndex}")
                action.tick(controller, deck, keyIndex)