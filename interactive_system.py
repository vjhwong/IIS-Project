from furhat_remote_api import FurhatRemoteAPI
from detect_faces import detect_emotion 
import time
import threading

def furhat_interaction():
    while True:
        #remember that is an array
        emotion=detect_emotion()[0]


        if emotion == "happy":
            furhat.say(text="Hello! I'm happy.")
            # Add more actions specific to happy emotion
        elif emotion == "sad":
            furhat.say(text="Hello... I'm feeling a bit down.")
            # Add more actions specific to sad emotion
        else:
            furhat.say(text="Hello! How can I help you today?")
        time.sleep(5)  # Sleep for 5 seconds


if __name__ == "__main__":
    furhat = FurhatRemoteAPI("localhost")
    voices = furhat.get_voices()
    furhat.set_voice(name='Matthew')


    furhat.say(text="Hi there!")
    interaction_thread = threading.Thread(target=furhat_interaction)
    interaction_thread.start()
