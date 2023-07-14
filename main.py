from controller import *
from gui import *
import threading
from time import sleep

def runApp():
    print("started app thread")
    #exit()
    app.run(sys.argv)

if __name__ == "__main__":
    communicationHandler = CommunicationHandler()
    app = StreamControllerApp(communicationHandler=communicationHandler, application_id="com.core447.StreamController")
    communicationHandler.app = app


    #appThread = threading.Thread(target=app.run, args=(sys.argv))
    #appThread.start()

    t = threading.Thread(target=runApp)
    t.start()

 


    communicationHandler.loadPlugins()
    communicationHandler.loadActionIndex()
    communicationHandler.initDecks()
    
    

    print("------- end of main.py ----------")

    #communicationHandler.closeDecks(reset=True)

    #while True: pass

