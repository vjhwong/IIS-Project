from furhat_remote_api import FurhatRemoteAPI
from detect_faces import detect_emotion 
import time
import threading

furhat = None
def set_furhat():
    furhat = FurhatRemoteAPI("localhost")
    voices = furhat.get_voices()
    furhat.set_voice(name='Matthew')
    return furhat

def furhat_interaction(emotion):
        #remember that is an array
        emotion=detect_emotion()
        if len(emotion) != 0:
            emotion = emotion[0]

        print(emotion)
        if emotion == "happy":
            furhat.say(text="Hello! I'm happy.")
            # Add more actions specific to happy emotion
        elif emotion == "sad":
            furhat.say(text="Hello... I'm feeling a bit down.")
            # Add more actions specific to sad emotion
        else:
            furhat.say(text="Hello! How can I help you today?")
        time.sleep(5)  # Sleep for 5 seconds


