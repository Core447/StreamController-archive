import os
import threading
import json
import ast

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

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
    return int(keyName[0]) + int(keyName[1])*5


def loadButton(deck, keyName, imagePath, captions, font):
    print(imagePath)
    print(f"KeyName: {keyName}")
    image = createDeckImage(deck, imagePath, font, captions)
    deck.set_key_image(keyNameToIndex(keyName), image)



def loadPage(deck, name: str):
    filepath = os.path.join("pages", name + ".json")
    with open(filepath) as file:
        data = json.load(file)

    print(data)
    deck.reset()

    buttons = data["buttons"]

    for button in buttons.items():
        #print(buttons[button[0]]["default-image"])
        loadButton(deck, button[0], buttons[button[0]]["default-image"], buttons[button[0]]["captions"], "Roboto-Regular.ttf")
        



if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):       

        deck.open()
        deck.reset()
        loadPage(deck, "main")
        exit()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
        ))

        # Set initial screen brightness to 30%.
        deck.set_brightness(30)

        with deck:
            image = render_key_image(deck, "Assets/Exit.png", "Roboto-Regular.ttf", "Test")
            #image = Image.open("")
            deck.set_key_image(0, image)