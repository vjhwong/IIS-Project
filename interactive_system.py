import numpy
from furhat_remote_api import FurhatRemoteAPI
import time
import threading

global furhat

START_EMOTION_REPLY = {
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
            reply = START_EMOTION_REPLY.get(em[0])
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

def is_happy_by_emotion(queue, lock):
    em = get_an_emotion(queue, lock)
    if len(em) != 0 and (em[0] is not None or em[0] != ''):
        if (em[0] == 'angry' or em[0] == 'disgust'):
            furhat.say(text="I see you don't want to do this. Do you want to try something different?")
            result = furhat.listen()
            if "yes" in result.message:
                return False
    return True

def does_user_want_to_stop(queue, lock):
    if listen_for_stop_in_response():
        return True
    if not is_happy_by_emotion(queue, lock):
        return True
    return False

def listen_for_stop_in_response():
    result = furhat.listen()
    if "stop" in result.message:
        furhat.say(text="I heard stop. Do you want to stop?")
        result = furhat.listen()
        if "yes" in result.message:
            return True
    return False



def meditation_for_happiness(name, furhat, lock, queue):
    #https://jackcanfield.com/blog/happiness-meditation/
    furhat.say(text="Here's a simple guided meditation for happiness. Can we start?")
    result = furhat.listen()
    if "yes" in result.message:
        furhat.say(text="Please, identify yourself with a name and a password.")
        time.sleep(2)
    if "how long" in result.message:
        furhat.say(text="This meditation is for 10 minutes.")
    if "other choice" in result.message or "something different" in result.message:
        furhat.say(text="Do you want to try something different?") #TODO sth different
    if "no" in result.message:
        furhat.say(text="I caught that you don't want to do this. Do you want to try something different?")

    does_user_want_to_stop(queue, lock)

    furhat.say(text="Sit for a moment and take a few long inhalations and exhalations. Focus on the breathing.")
    time.sleep(5)
    does_user_want_to_stop(queue, lock)
    furhat.say(text="Breath in slowly and breath out slowly.")
    time.sleep(5)
    does_user_want_to_stop(queue, lock)
    furhat.say("CLear your mind. If you find your thoughts shifting from the breathing, gently release that thought and concentrate on breathing.")
    time.sleep(5)
    does_user_want_to_stop(queue, lock)
    furhat.say("Think of your thoughts as train cars passing through the station. You’re on the platform, watching them go past.")
    time.sleep(10)
    does_user_want_to_stop(queue, lock)

    furhat.say("Your mind should be quiet now. Let's thank to what you're experiencing.")
    furhat.say("Give thanks to your mind, which allows you to think of all your thoughts. ")
    time.sleep(2)
    does_user_want_to_stop(queue, lock)
    furhat.say("Be grateful for your eyes, that allow you to see the world’s beauty. "
               "Give thanks to your ears that allow you to hear the world’s music, and then to your mouth "
               "that allows you to taste the world’s deliciousness in all its myriad forms.")
    time.sleep(5)
    furhat.say("Be grateful for your arms and your hands and all they allow you to do.")
    time.sleep(2)
    furhat.say("Such as holding a child, reaching out and grabbing something to you, throwing a ball or a pillow, \
               catching a ball or your falling child, writing a book, typing a report, driving a car, "
               "playing a musical instrument, creating a piece of art, cooking a meal, or hugging a loved one, "
               "or making love.")
    time.sleep(5)
    does_user_want_to_stop(queue, lock)
    furhat.say("Be grateful for your lungs, for allowing you to breathe, and for your throat, for allowing you to speak and sing. "
               "And be grateful for your legs and feet, for making it possible for you to walk, run, jump, and dance.")
    time.sleep(10)
    does_user_want_to_stop(queue, lock)

    furhat.say("Be grateful for the chair you’re sitting on, and the people who put their time and effort into making that chair. "
               "Be grateful for the money that allowed you to buy that chair, or the person who gave it to you.")
    time.sleep(5)
    does_user_want_to_stop(queue, lock)
    furhat.say("Be grateful for the coffee cup beside you, and the delicious coffee it used to hold "
               "that’s now flowing through your veins, making you feel more awake and alert.")
    time.sleep(2)
    furhat.say("Be grateful for the clothes that you’re wearing, and the person who made those clothes, "
               "and the job that gave you the money you needed to buy them.")
    time.sleep(2)
    does_user_want_to_stop(queue, lock)

    furhat.say("Be grateful for your home, and your family and your friends. "
               "Be grateful for the people who make your life better or easier in some way—"
               "like the people at the grocery store, the gas station, the coffee shops, and the restaurants—the garbage men, "
               "the taxi drivers and Uber drivers, the weathermen and women, the doctors, nurses, healers and holistic practitioners.")
    time.sleep(5)
    does_user_want_to_stop(queue, lock)

    furhat.say("Be grateful for the city and the country you live in, and the freedoms and rights that are available to you. "
               "Be grateful for the natural world around you—the birds that you hear out the window, the flowers and the trees, "
               "the parks and the bodies of water, and the fish that swim the ocean. ")
    time.sleep(5)
    does_user_want_to_stop(queue, lock)

    furhat.say("Expand your gratitude to whatever you can think of. You can even feel gratitude for the planet, the solar system, the stars, and even for life itself!")
    furhat.say("Gently let your mind drift from topic to topic, while consciously practicing gratitude for everything that occurs to you.")
    furhat.say("Try to maintain this state for about 5 minutes if you can.")
    does_user_want_to_stop(queue, lock)

    result = furhat.listen(timeout = 5*60000)
    if result != '':
        furhat.say("Do you want to stop?")
        result = furhat.listen()
        if "yes" in result.message:
            return False #TODO stop

    furhat.say("Open your eyes.")
    time.sleep(1)
    furhat.say("Now, take a moment to acknowledge the joy that comes with showing this kind of gratitude.")
    time.sleep(1)
    furhat.say("It is important to pause and recognize that small, incremental changes in your daily life can build up "
               "and make larger improvements in your mental health.")
    time.sleep(2)
    furhat.say("This simple meditation can have a huge impact on your mindset and your vibration. "
               "If you return to me tomorrow as well, you will find it so much easier to experience more joy and happiness in your life.")
    time.sleep(2)

    furhat.say("Thank you for spending time with me. Did this session help?")
    result = furhat.listen()
    if "yes" in result:
        furhat.say("I'm glad this helped. Hope to see you tomorrow.")
    else:
        furhat.say(text="Do you want to try something different?")
            #TODO sth different

