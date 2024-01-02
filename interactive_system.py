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

def stopped_if_user_wants_to_stop(queue, lock):
    if does_user_want_to_stop(queue, lock):
        furhat.say(text="I caught that you don't want to do this. Do you want to try something different?")
        result = furhat.listen()
        if "yes" in result.message:
            furhat.say(text="Let's try something different then!")
            return True
        else:
            furhat.say(text="Let's continue then!")
            return False


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

def breathing_excercices(name, furhat, lock, queue):
    #https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/
    furhat.say(text="Here's a simple breathing excercise. Can we start? ")
    result = furhat.listen()
    if "yes" in result.message:
        furhat.say(text="Let's start. If you wish to stop at any time, you can just say so.")
        time.sleep(2)
    if "how long" in result.message:
        furhat.say(text="This breathing exercise takes just a few minutes.")
    if "other choice" in result.message or "something different" in result.message:
        furhat.say(text="Do you want to try something different?")  # TODO sth different
    if "no" in result.message:
        furhat.say(text="I caught that you don't want to do this. Do you want to try something different?")

    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say(text="You can do it standing up, sitting in a chair that supports your back, or lying on a bed or yoga mat on the floor.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="Make yourself as comfortable as you can. If you can, loosen any clothes that restrict your breathing.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="If you're lying down, place your arms a little bit away from your sides, with the palms up. Let your legs be straight, "
             "or bend your knees so your feet are flat on the floor.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="If you're sitting, place your arms on the chair arms.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="If you're sitting or standing, place both feet flat on the ground. Whatever position you're in, "
             "place your feet roughly hip-width apart.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say(
        text="Let your breath flow as deep down into your belly as is comfortable, without forcing it.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="Try breathing in through your nose and out through your mouth.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="Breathe in gently and regularly. Some people find it helpful to count steadily from 1 to 5. You may not be able to reach 5 at first.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="Then let it flow out gently, counting from 1 to 5 again, if you find this helpful.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(
        text="Now, repeat this for at least five minutes. I will be notifying you about the time")

    iteration = 1
    for i in range(5):
        result = furhat.listen(timeout=1 * 60000)
        if result != '':
            furhat.say("Do you want to stop?")
            result = furhat.listen()
            if "yes" in result.message:
                return False  # TODO stop
        if iteration == 1:
            furhat.say(
                text= str(iteration) + " minute has passed. Let's keep doing this, you're doing great!")
        else:
            furhat.say(
                text=str(iteration) + " minutes has passed. Let's keep doing this, you're doing great!")
        iteration += 1

    furhat.say(
        text="You've finished this breathing exercise. You will get the most benefit if you do it regularly, as part of your daily routine.")

    #TODO check emotions here? or later?
    furhat.say("Thank you for spending time with me. Did this session help?")
    result = furhat.listen()
    if "yes" in result:
        furhat.say("I'm glad this helped. Hope to see you tomorrow.")
    else:
        furhat.say(text="Do you want to try something different?")
        # TODO sth different

def say_camforting_story(furhat, lock, queue):
    furhat.say("To understand you better, what happened? Is this work related or school related? Or about relationships?")
    caught_answer = False

    while not caught_answer:
        result = furhat.listen()
        if "work" in result:
            furhat.say(
                "I see. You can tell me more if you wish.")
            time.sleep(2)
            result = furhat.listen()
            if "colleague" in result:
                furhat.say(
                    "You can try talk to this colleague")
                time.sleep(2)
            if "boss" in result:
                furhat.say(
                    "You can try talk to your boss about your situation")
                time.sleep(2)
            if "stress" in result or "hard" in result or "difficult" in result or "exhausted" in result or "exhausting" in result or "overtime" in result:
                #https://www.helpguide.org/articles/stress/stress-in-the-workplace.htm
                furhat.say(
                    "Try reach out to someone if you find your job position too stressful. "
                    "You should also support your health with exercise and nutrition. Don't skimp on sleep instead, try to go to bed early. And create a balanced schedule, leave earlier in the mornings and plan regular breaks.")
                time.sleep(2)
            elif result != "":
                furhat.say(
                    "I understand. That is a difficult situation. But remember, challenges are what make life interesting"
                    "and overcoming them is what makes life meaningful.")
                time.sleep(2)
                result = furhat.listen()
        if "school" in result or "uni" in result or "university" or "college" in result in result or "teacher" in result or "classmate" in result:
            pass
        if "friendship" in result or "friend" in result:
            furhat.say(
                "I see. You can tell me more if you wish.")
            time.sleep(2)
            result = furhat.listen()
            if "lonely" in result or "no friend" in result or "don't have any friend" in result or "zero friends" in result:
                # https://www.verywellmind.com/i-have-no-friends-what-to-do-5200867
                furhat.say(
                    "Having no friends is a common difficulty many people suffer no matter the age.")
                time.sleep(2)
                furhat.say(
                    "Sometimes, it is not easy to make friends. Either you're shy or have social anxiety, there can be many reasons.")
                time.sleep(2)
                furhat.say(
                    "But you should not be afraid to meet new people or rejection. You just may not connect with every person you talk to and that's okay.")
                time.sleep(2)
                furhat.say(
                    "Find people who have similar interests. Try to join some clubs. You enjoy reading? Join a reading club!"
                    " You enjoy playing football? Join a football club! You get the gist") #TODO wink
                time.sleep(2)
                furhat.say(
                    "Try volunteering. Be friendly, be open-minded and truthful when asked question.")
                time.sleep(2)
                furhat.say(
                    "And just try to talk to people. There are other people like you looking for friends."
                    "Ask about their interests and try to find something that you might have in common.")
                time.sleep(2)
            elif "fight" in result or "disagree" in result:
                #https://kidshelpline.com.au/teens/issues/fights-friends
                furhat.say(
                    "If you had a fight with your friend or you disagree on something, you can talk it out. "
                    "Try to reach out to your friend. Stay calm and respectful. Acknowledge their feelings and listen. "
                    "Take time out and don't pull others in. You will sort it out.")
                time.sleep(5)
            elif result != "":
                furhat.say(
                    "I understand. That is a difficult situation. But remember, challenges are what make life interesting"
                    "and overcoming them is what makes life meaningful.")
                time.sleep(2)
        if "love" in result or "boyfriend" in result or "girlfriend" in result or "relationship" in result:
            furhat.say(
                "I see. You can tell me more if you wish.")
            time.sleep(2)
            result = furhat.listen()
            if "lonely" in result or "no love" in result or "don't have anyone" in result or "no boyfriend" in result or "no gilfreind" in result or "want" in result:
                furhat.say(
                    "I'll quote Lucille Ball here. Love yourself first and everything else falls into line. "
                    "You really have to love yourself to get anything done in this world.")
                time.sleep(2)
            elif "fight" in result or "disagree" in result:
                #https://kidshelpline.com.au/teens/issues/fights-friends
                furhat.say(
                    "If you had a fight with your friend or you disagree on something, you can talk it out. "
                    "Try to reach out to your friend. Stay calm and respectful. Acknowledge their feelings and listen. "
                    "Take time out and don't pull others in. You will sort it out.")
                time.sleep(5)
            elif result != "":
                furhat.say(
                    "I understand. That is a difficult situation. But remember, challenges are what make life interesting"
                    "and overcoming them is what makes life meaningful.")
        else:
            pass


def meditation_for_happiness(name, furhat, lock, queue):
    #https://jackcanfield.com/blog/happiness-meditation/
    furhat.say(text="Here's a simple guided meditation for happiness. Can we start? ")
    result = furhat.listen()
    if "yes" in result.message:
        furhat.say(text="Let's start. If you wish to stop at any time, you can just say so.")
        time.sleep(2)
    if "how long" in result.message:
        furhat.say(text="This meditation is for 10 minutes.")
    if "other choice" in result.message or "something different" in result.message:
        furhat.say(text="Do you want to try something different?") #TODO sth different
    if "no" in result.message:
        furhat.say(text="I caught that you don't want to do this. Do you want to try something different?")

    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say(text="Sit for a moment and take a few long inhalations and exhalations. Focus on the breathing.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say(text="Breath in slowly and breath out slowly.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say("CLear your mind. If you find your thoughts shifting from the breathing, gently release that thought and concentrate on breathing.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say("Think of your thoughts as train cars passing through the station. You’re on the platform, watching them go past.")
    time.sleep(10)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say("Your mind should be quiet now. Let's thank to what you're experiencing.")
    furhat.say("Give thanks to your mind, which allows you to think of all your thoughts. ")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
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
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say("Be grateful for your lungs, for allowing you to breathe, and for your throat, for allowing you to speak and sing. "
               "And be grateful for your legs and feet, for making it possible for you to walk, run, jump, and dance.")
    time.sleep(10)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say("Be grateful for the chair you’re sitting on, and the people who put their time and effort into making that chair. "
               "Be grateful for the money that allowed you to buy that chair, or the person who gave it to you.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return
    furhat.say("Be grateful for the coffee cup beside you, and the delicious coffee it used to hold "
               "that’s now flowing through your veins, making you feel more awake and alert.")
    time.sleep(2)
    furhat.say("Be grateful for the clothes that you’re wearing, and the person who made those clothes, "
               "and the job that gave you the money you needed to buy them.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say("Be grateful for your home, and your family and your friends. "
               "Be grateful for the people who make your life better or easier in some way—"
               "like the people at the grocery store, the gas station, the coffee shops, and the restaurants—the garbage men, "
               "the taxi drivers and Uber drivers, the weathermen and women, the doctors, nurses, healers and holistic practitioners.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say("Be grateful for the city and the country you live in, and the freedoms and rights that are available to you. "
               "Be grateful for the natural world around you—the birds that you hear out the window, the flowers and the trees, "
               "the parks and the bodies of water, and the fish that swim the ocean. ")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say("Expand your gratitude to whatever you can think of. You can even feel gratitude for the planet, the solar system, the stars, and even for life itself!")
    furhat.say("Gently let your mind drift from topic to topic, while consciously practicing gratitude for everything that occurs to you.")
    furhat.say("Try to maintain this state for about 5 minutes if you can.")
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

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
               "If you practice this excercise tomorrow as well, you will find it so much easier to experience more joy "
               "and happiness in your life.")
    time.sleep(2)

    furhat.say("Thank you for spending time with me. Did this session help?")
    result = furhat.listen()
    if "yes" in result:
        furhat.say("I'm glad this helped. Hope to see you tomorrow.")
    else:
        furhat.say(text="Do you want to try something different?")
            #TODO sth different

