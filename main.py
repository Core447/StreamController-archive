from controller import *
from gui import *

if __name__ == "__main__":
    communicationHandler = CommunicationHandler()
    communicationHandler.loadPlugins()
    communicationHandler.loadActionIndex()
    communicationHandler.initDecks()

    app = StreamControllerApp(communicationHandler=communicationHandler, application_id="com.core447.StreamController")
    app.run(sys.argv)

    print("resetting")

    communicationHandler.closeDecks(reset=True)

    #while True: pass