import os
import threading
import json
import ast
import math

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
import StreamDeck
import time

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")


def createDeckImage(deck, icon_filename, font_filename, captions):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(os.path.join(ASSETS_PATH, "images", icon_filename))
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0], background=((0,0,0)))

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    

    #load json from string
    captions = str(captions).replace("'",'"')
    captions = json.loads(captions)
    
    
    for caption in captions:
        #Load font
        font = ImageFont.truetype(os.path.join(ASSETS_PATH, "fonts", font_filename), 14)
        #Draw captions on to the image
        draw.text((image.width / 2, image.height*caption[0]["text-location"]), text=caption[0]["text"], font=font, anchor="ms", fill="white")
    
    return PILHelper.to_native_format(deck, image)

def keyNameToIndex(keyName):
    keyName = keyName.split("x")
    return int(keyName[0]) + int(keyName[1])*deck.key_layout()[1]



        


class Controller:
    """
    The Controller class takes care of managing a deck.
    """
    def __init__(self, deck: StreamDeck.Devices):
        self.deck = deck
        self.deck.open()
        self.loadedPage = None
        self.loadedPageJson = None

        #Register callback function (handles key presses)
        deck.set_key_callback(self.keyChangeCallback)

    def loadPage(self, name: str):
        """
        Load a page with the given name.

        Args:
            name (str): The name of the page to load.

        Returns:
            None
        """
        
        self.deck.reset() #Reset the deck
        filepath = os.path.join("pages", name + ".json") #Load the corresponding page file
        with open(filepath) as file:
            data = json.load(file)

        buttons = data["buttons"]
        for button in buttons.items():
            self.loadButton(button[0], buttons[button[0]]["default-image"], buttons[button[0]]["captions"], "Roboto-Regular.ttf")

        self.loadPage = name
        self.loadedPageJson = self.getPageJson(name)

    def loadButton(self, keyName, imagePath, captions, font):
        image = createDeckImage(deck, imagePath, font, captions)
        self.deck.set_key_image(keyNameToIndex(keyName), image)

    def handleInputs(self):
        pass

    def tick(self):
        #self.handleInputs()
        pass

    def getPageJson(self, pageName):
        with open(os.path.join("pages", pageName + ".json")) as file:
            jsonData = json.load(file)
        return jsonData
    
    def getJsonKeySyntaxByIndex(self, keyIndex):
        row = keyIndex // deck.key_layout()[1]
        column = keyIndex % deck.key_layout()[1]

        return f"{row}x{column}"

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
        elif state == False and button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-release"] != "none":
            print(button[self.getJsonKeySyntaxByIndex(key)]["actions"]["on-release"])

       




if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):       

        controller = Controller(deck)
        controller.loadPage("main")
        print(controller.getJsonKeySyntaxByIndex(14))
        while True:
            controller.tick()
            time.sleep(0.1)

        