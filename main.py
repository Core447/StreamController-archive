import os
import threading
import json

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")


def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0], background=((0,0,0)))

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text((image.width / 2, image.height -5), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_format(deck, image)

def keyNameToIndex(keyName):
    keyName = keyName.split("x")
    return int(keyName[0]) + int(keyName[1])*5


#keyNameToIndex("1x2")
#exit()


def loadButton(deck, keyName, imagePath, captions):
    print(imagePath)
    print(f"KeyName: {keyName}")
    image = render_key_image(deck, imagePath, "Assets/Roboto-Regular.ttf","")
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
        loadButton(deck, button[0], buttons[button[0]]["default-image"], buttons[button[0]]["captions"])
        



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
            image = render_key_image(deck, "Assets/Exit.png", "Assets/Roboto-Regular.ttf", "Test")
            #image = Image.open("")
            deck.set_key_image(0, image)