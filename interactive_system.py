from furhat_remote_api import FurhatRemoteAPI
import time
import threading

global furhat

def set_furhat():
    furhat = FurhatRemoteAPI("localhost")
    voices = furhat.get_voices()
    furhat.set_voice(name='Matthew')
    return furhat

def furhat_interaction(emotion, furhat):
        #remember that is an array
        if len(emotion) != 0:
            emotion = emotion[0]

        furhat.say(text = "I can see you are " + emotion)
        #print(emotion)
        #if emotion == "happy":
        #    furhat.say(text="You look happy.")
        #elif emotion == "sad":
        #    furhat.say(text="You look sad.")
        #elif emotion == "angry":
        #    furhat.say(text="You look angry.")
        #elif emotion == "neutral":
        #    furhat.say(text="How are you feeling?")
        #else:
        #    furhat.say(text="Hello! How can I help you today?")


