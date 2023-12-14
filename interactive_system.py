import numpy
from furhat_remote_api import FurhatRemoteAPI
import time
import threading

global furhat

EMOTION_REPLY = {
    'fear' : 'Do you need any help? I can tell you authority numbers if you need them.',
    'surprise' : 'Surprised to see me? It’s been a long time',
    'angry' : 'I think something is disturbing your inner peace, what’s happened?',
    'happy' : 'I see you are in a good mood, have my last sessions helped?',
    'sad' : 'You seem sad, has anything happened since last time I saw you?',
    'neutral' : 'How have you been?',
    'disgust' : ''
}

def set_furhat():
    furhat = FurhatRemoteAPI("localhost")
    voices = furhat.get_voices()
    furhat.set_voice(name='Matthew')
    return furhat

def start_furhat(furhat):
    name = identification(furhat)
    return name

def furhat_interaction(emotion, furhat):
        #remember that is an array
        if len(emotion) != 0:
            emotion = emotion[0]

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
        furhat.say(text="Please, identify yourself with a name and a password.")
        time.sleep(2)
        while not identified:
            name, password = listen_to_name_and_password(furhat)
            if name is None:
                furhat.say(text="I didn't get that, can you repeat it?")
                time.sleep(1)
                continue
            if is_name_and_password_valid(name,password):
                identified = True
                furhat.say(text="Hello " + name + ". Welcome back! I'm happy to see you.")
            else:
                furhat.say(text="I'm sorry, I don’t seem to know " + name + " with that id, can you repeat it? " \
                                "Otherwise, a new profile will be created")
                time.sleep(2)
                result = furhat.listen()
                if "yes" in result.message:
                    furhat.say(text="Please, identify yourself with a name and a password.")
                    time.sleep(2)
    if not identified:
        furhat.say(text="Let's create a new profile for you. "
                        "Tell me your name and password you want to use for your identification. "
                        "Say it slow in order name and password")
        time.sleep(5)
    while not identified:
        name, password = listen_to_name_and_password(furhat)
        if name is None:
            furhat.say(text="I didn't get that, can you repeat it?")
            time.sleep(1)
            continue
        save_name_and_password(name, password)
        furhat.say(text="Hello " + name + ", your new profile has been created! I am excited to start our new journey.") #TODO check if the name is correct
        identified = True
    return name

def listen_to_name_and_password(furhat):
    result = furhat.listen()
    print("message is : " + result.message)
    if result.message is None or result.message == '':
        return None, None
    if ' ' not in result.message:
        return None, None
    name, password = result.message.split()
    print(name, password)
    if name == '' or name is None or password == '' or password is None:
        return None, None
    return name, password

def save_name_and_password(name, password):
    pass

def is_name_and_password_valid(name,password):
    return True

def run_conversation_loop(name, furhat, queue):
    lock = threading.Lock()
    conversation_ended = False
    while not conversation_ended:
        em = get_an_emotion(queue, lock)
        if len(em) != 0 and (em[0] is not None or em[0] != ''):
            reply = EMOTION_REPLY.get(em[0])
            furhat.say(text=reply)
        time.sleep(5)


def get_an_emotion(queue, lock):
    with lock:
        em = queue.get()
    # em = predict_emotion(aus, model)
    print("controller emotion " + em, flush=True)
    #print(list(queue.queue))
    #if em is not None or em != '':
    return em