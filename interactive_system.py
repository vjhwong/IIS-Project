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

        name = identification(furhat)
        start_a_conversation(name, furhat)

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

def identification(furhat):
    furhat.say(text="Do you have an identification?")
    result = furhat.listen()
    identified = False
    name = ''
    if "yes" in result.message:
        furhat.say(text="Please, identify yourself with a name and a password")
        while not identified:
            result = furhat.listen()
            name,password = result.message.split()
            if is_name_and_password_valid(name,password):
                identified = True
                furhat.say(text="Hello " + name + "Welcome back! I'm happy to see you.")
            else:
                furhat.say(text="I'm sorry, I don’t seem to know you, " + name + " or that id, can you repeat it? " \
                                "If you say 'no' a new profile will be created?")
                result = furhat.listen()
                if "yes" in result.message:
                    continue
    if not identified:
        furhat.say(text="Let's create a new profile for you. " \
                        "Tell me your name and password you want to use for your identification in this order.")
        result = furhat.listen()
        name, password = result.message.split()
        save_name_and_password(name, password)
        furhat.say(text="Hello " + name + ", your new profile has been created! I am excited to start our new journey.")
    return name

def save_name_and_password(name, password):
    pass

def is_name_and_password_valid(name,password):
    return True

def start_a_conversation(name, furhat):
    pass
