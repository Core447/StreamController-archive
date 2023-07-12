"""
Reset all connected StreamDecks
"""

from StreamDeck.DeviceManager import DeviceManager

# Get a list of all connected StreamDeck devices
decks = DeviceManager().enumerate()

# Print the list of connected devices
print(decks)

# Iterate through each device
for deck in decks:
    # Open the device
    deck.open()

    # Reset the device
    deck.reset()

    # Close the device
    deck.close()
