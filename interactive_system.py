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

# TODO if user doesn't understand, repeat what furhat said

def identification(furhat):
    answered = False
    while not answered:
        furhat.say(text="Do you have an identification?")
        result = furhat.listen()
        identified = False
        name = ''

        if "skip" in result.message:
            # for testing purposes as well as the user might want to enter anonymous mode
            return "Eve"

        if "yes" in result.message:
            furhat.say(text="Please, identify yourself with a name and a password.")
            time.sleep(2)
            while not identified:
                name, password = listen_to_name_and_password(furhat)
                if name is None:
                    furhat.say(text="I didn't get that, would you like to repeat it " \
                                    "or do you want to create a new profile?")
                    time.sleep(2)
                    result = furhat.listen()
                    if "repeat" in result.message or "again" in result.message:
                        furhat.say(text="Please, identify yourself with a name and a password.")
                        time.sleep(2)
                    continue
                if is_name_and_password_valid(name,password):
                    identified = True
                    furhat.say(text="Hello " + name + ". Welcome back! I'm happy to see you.")
                else:
                    furhat.say(text="I'm sorry, I don’t seem to know " + name + " with that password, would you like to repeat it " \
                                    "or do you want to create a new profile?")
                    time.sleep(2)
                    result = furhat.listen()
                    if "repeat" in result.message or "again" in result.message:
                        furhat.say(text="Please, identify yourself with a name and a password.")
                        time.sleep(2)
        else:
            if furhat_should_repeat_itself(result.message):
                continue
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

def furhat_should_repeat_itself(message):
    if message == '' or user_wants_to_repeat_what_furhat_said(message):
        return True
    return False

def user_wants_to_repeat_what_furhat_said(message):
    if "what" in message or "sorry" in message or "say it again" in message or "can you repeat it" in message or "repeat yourself" in message:
        return True
    return  False

def listen_to_name_and_password(furhat):
    result = furhat.listen()
    print("message is : " + result.message)
    if result.message is None or result.message == '' or len(result.message.split()) != 2:
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
    time.sleep(5)
    lock = threading.Lock()
    conversation_ended = False
    first_interaction = True
    done_exercises = [] #TODO fill list somewhere
    while not conversation_ended:
        em = get_an_emotion(queue, lock)
        if len(em) != 0 and (em[0] is not None or em[0] != ''):
            if first_interaction:
                reply = START_EMOTION_REPLY.get(em[0])
                time.sleep(2)
                furhat.say(text=reply)
                result = furhat.listen() #TODO do sth with the result
                first_interaction = False
                was_happy = start_interaction_based_on_emotion(name, furhat, queue, em[0], lock)
                if not was_happy:
                    was_happy = offer_options(name, furhat, queue, lock)
                    # TODO what to do now? if user wants to end
            else:
                furhat.say("Is there anything else I can do for you?")

                # TODO recommend based on emotion
                wants_exercise_by_emotion = user_wants_to_do_exercise_based_on_emotion(em[0], done_exercises)
                if wants_exercise_by_emotion:
                    start_interaction_based_on_emotion(name, furhat, queue, em[0], lock)
                    continue

                furhat.say("Do you want me to list you options of other exercises?")
                time.sleep(2)
                result = furhat.listen()
                result = result.message

                if "yes" in result or "list" in result or "options" in result or "different" in result:
                    was_happy = offer_options(name, furhat, queue, lock)
                    # TODO what to do now? if user wants to end
                elif "end" in result or "stop" in result or "leave" in result:
                    break

            # TODO
        time.sleep(5)
    furhat.say("Thank you for spending time with me. Hope to see you next time! Have a great day!")
    #TODO save user happiness and stats

def user_wants_to_do_exercise_based_on_emotion(emotion, done_exercises):
    match emotion:
        case 'fear':
            pass
            # TODO
        case 'surprise':
            pass
            # TODO
        case 'angry':
            if breathing_excercice.__name__ in done_exercises:
                return False
            else:
                furhat.say("I would recommend breathing exercise. Do you want to start that?")
        case 'happy':
            if meditation_for_happiness.__name__ in done_exercises:
                return False
            else:
                furhat.say("I would recommend meditation for happiness. Do you want to start that?")
        case 'sad':
            if breathing_excercice.__name__ in done_exercises:
                return False
            else:
                furhat.say("I would recommend breathing exercise for happiness. Do you want to start that?")
        case 'neutral':
            if mindfulness_exercise.__name__ in done_exercises:
                return False
            else:
                furhat.say("I would recommend mindfulness exercise for happiness. Do you want to start that?")
        case 'disgust':
            pass

    time.sleep(2)
    result = furhat.listen()
    result = result.message
    if "don't start" in result or "stop" in result or "no" in result:
        return False
    else:
        return True


def start_interaction_based_on_emotion(name, furhat, queue, emotion, lock):
    furhat.say("I will pick an exercise specifically selected for you right now.")
    time.sleep(2)
    match emotion:
        case 'fear':
            pass
            # TODO
        case 'surprise':
            pass
            # TODO
        case 'angry':
            return breathing_excercice(name, furhat, lock, queue)
        case 'happy':
            return meditation_for_happiness(name, furhat, lock, queue)
        case 'sad':
            say_comforting_story(furhat, lock, queue)
            return breathing_excercice(name, furhat, lock, queue)
        case 'neutral':
            return mindfulness_exercise(name, furhat, lock, queue)
        case 'disgust':
            pass
            # TODO

def offer_options(name, furhat, queue, lock):
    picked_exercise = False

    while not picked_exercise:
        furhat.say("I caught that you want to try something different. We can do: " \
                   "breathing exercise, " \
                   "meditation for happiness, " \
                   "we can just talk, I can listen to what's on your mind and say few comforting words," \
                   "mindfulness exercises, I can list them if you'd like. " \
                   "So, what will it be? If you'd like to leave, you can just tell me to stop.")
        time.sleep(5)
        # TODO tell more about each
        result = furhat.listen()
        result = result.message
        if "first" in result or "breathing exercise" in result:
            picked_exercise = True
            furhat.say("Do you want to know more or start or try something different?")
            if "option" in result or "choice" in result.message or "different" in result.message:
                continue
            if "more" in result:
                # TODO explain breathing exercise
                pass
            # leave option is done outside the if block
            return breathing_excercice(name, furhat, queue, lock)
        elif "second" in result or "meditation for happiness" in result or "meditation" in result or "happiness" in result:
            picked_exercise = True
            furhat.say("Do you want to know more or start or try something different?")
            if "option" in result or "choice" in result.message or "different" in result.message:
                continue
            if "more" in result:
                # TODO explain meditation
                pass
            # leave option is done outside the if block
            return meditation_for_happiness(name, furhat, lock, queue)
        elif "third" in result or "talk" in result or "listen" in result or "comforting" in result:
            picked_exercise = True
            furhat.say("Do you want to know more or start or try something different?")
            if "option" in result or "choice" in result.message or "different" in result.message:
                continue
            if "more" in result:
                # TODO explain listening and comforting
                pass
            return say_comforting_story(furhat, lock, queue)
        elif "last" in result or "fifth" in result or "mindfulness exercise" in result or "list" in result:
            picked_exercise = True
            furhat.say("Do you want to know more or start or try something different?")
            if "option" in result or "choice" in result.message or "different" in result.message:
                continue
            if "more" in result:
                # TODO explain mindfulness exercise
                pass

            picked_option = False
            while not picked_option:
                furhat.say("There are multiple exercises you can try. "
                           "mindful breathing, body scan, five senses exercise, walking meditation, and gratitude list. "
                           "Which one do you want to try?")
                time.sleep(5)
                result = furhat.listen()
                if "first" in result or "mindful breathing" in result:
                    picked_option = True
                    return mindful_breathing(furhat, lock, queue)
                elif "second" in result or "body scan" in result:
                    picked_option = True
                    return body_scan(furhat, lock, queue)
                elif "third" in result or "five senses" in result:
                    picked_option = True
                    return five_senses_exercise(furhat, lock, queue)
                elif "fourth" in result or "walking meditation" in result:
                    picked_option = True
                    return walking_meditation(furhat, lock, queue)
                elif "last" in result or "fifth" in result or "gratitude list" in result:
                    picked_option = True
                    return gratitude_list(furhat, lock, queue)
                elif "again" in result:
                    continue
                elif "stop" in result or "end" in result:
                    break
                else:
                    furhat.say("I'm sorry, I didn't catch that. Let me repeat the options again.")
        elif "leave" not in result or "stop" not in result or "end" not in result:
            furhat.say("I'm sorry, I didn't catch that. Let me repeat the options again.")

        if "leave" in result or "stop" in result or "end" in result:
            break
            # TODO stop

def get_an_emotion(queue, lock):
    with lock:
        em = queue.get()
    # em = predict_emotion(aus, model)
    print("controller emotion " + em, flush=True)
    #print(list(queue.queue))
    #if em is not None or em != '':
    return em

def is_happy_by_emotion(queue, lock): #TODO add original emotion so that if person is angry at the beginning, it won't stop like this
    em = get_an_emotion(queue, lock)
    if len(em) != 0 and (em[0] is not None or em[0] != ''):
        if (em[0] == 'angry' or em[0] == 'disgust'):
            furhat.say(text="I see you don't want to do this. Do you want to try something different?")
            result = furhat.listen()
            if "yes" in result.message:
                return False
    return True

def stopped_if_user_wants_to_stop(queue, lock): # TODO what if the user wants to stop the whole session?
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
    if "stop" in result.message or "end" in result.message or "leave" in result.message:
        furhat.say(text="I heard stop. Do you want to stop?")
        result = furhat.listen()
        if "yes" in result.message:
            return True
    return False

def breathing_excercice(name, furhat, lock, queue):
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

def say_comforting_story(furhat, lock, queue):
    furhat.say("To understand you better, what happened? Is this work related or school related? Or about relationships?")
    caught_answer = False

    while not caught_answer:
        result = furhat.listen()
        if "work" in result:
            caught_answer = True
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
                furhat.say("You can try some of my relaxing meditations or breathing exercises.")
                time.sleep(2)
            elif result != "":
                furhat.say(
                    "I understand. That is a difficult situation. But remember, challenges are what make life interesting"
                    "and overcoming them is what makes life meaningful.")
                time.sleep(2)
                result = furhat.listen()
        if "school" in result or "uni" in result or "university" or "college" in result in result or "teacher" in result or "classmate" in result:
            caught_answer = True
            furhat.say(
                "I see. You can tell me more if you wish.")
            time.sleep(2)
            result = furhat.listen()
            if "classmate" in result:
                furhat.say(
                    "You can try talk to this colleague")
                time.sleep(2)
            if "teacher" in result:
                furhat.say(
                    "You can try talk to your teacher or another authority about your situation")
                time.sleep(2)
            if "stress" in result or "hard" in result or "difficult" in result or "exhausted" in result or "exhausting" in result or "marks" in result:
                # https://www.helpguide.org/articles/stress/stress-in-the-workplace.htm
                furhat.say(
                    "Try reach out to someone if you find the school too stressful or too demanding. "
                    "You should also support your health with exercise and nutrition. Don't skimp on sleep instead, try to go to bed early. And create a balanced schedule, leave earlier in the mornings and plan regular breaks.")
                furhat.say("You can try some of my relaxing meditations or breathing exercises.")
                time.sleep(2)
            elif result != "":
                furhat.say(
                    "I understand. That is a difficult situation. But remember, challenges are what make life interesting"
                    "and overcoming them is what makes life meaningful.")
                time.sleep(2)
                result = furhat.listen()
        if "friendship" in result or "friend" in result:
            caught_answer = True
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
            caught_answer = True
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
        elif "stop" in result or "end" in result:
            furhat.say(text="I caught that you don't want to do this. Do you want to try something different?")
            #TODO something different
        else:
            furhat.say(
                "I didn't catch that. Can you repeat it, please?")


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
        furhat.say(text="I caught that you don't want to do this. Do you want to try something different?")#TODO something different

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

def mindfulness_exercise(name, furhat, lock, queue):
    furhat.say(text="Here's a simple guided mindfulness exercise. Can we start? ")
    result = furhat.listen()
    if "yes" in result.message:
        furhat.say(text="Let's start. If you wish to stop at any time, you can just say so.")
        time.sleep(2)
    if "how long" in result.message:
        furhat.say(text="This exercise takes about 10 minutes.")
    if "other choice" in result.message or "something different" in result.message:
        furhat.say(text="Do you want to try something different?")  # TODO sth different
    if "no" in result.message:
        furhat.say(
            text="I caught that you don't want to do this. Do you want to try something different?")  # TODO something different


def mindful_breathing(furhat, lock, queue):
    # https://www.verywellhealth.com/mindfulness-exercises-5204406 and https://www.healthline.com/health/box-breathing#hold-your-breath

    furhat.say("This technique can be beneficial to anyone, especially those who want to meditate or reduce stress.")
    furhat.say(
        "Make sure that you’re seated upright in a comfortable chair with your feet flat on the floor. Try to be in a stress-free, quiet environment where you can focus on your breathing.")
    furhat.say("Keeping your hands relaxed in your lap with your palms facing up, focus on your posture.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

    furhat.say("Breathe in through your nose for a count of 4. Feel the air fill your lungs, one section at a time, until your lungs are completely full and the air moves into your abdomen.")
    time.sleep(4)
    furhat.say("Now hold for another 4 seconds")
    time.sleep(4)
    furhat.say("Exhale through your mouth for a count of 4. Be conscious of the feeling of the air leaving your lungs.")
    time.sleep(4)
    furhat.say("Now hold for another 4 seconds")
    time.sleep(4)
    furhat.say("Repeat until you want to stop.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

def body_scan(furhat, lock, queue):
    #https://www.mayoclinic.org/healthy-lifestyle/consumer-health/in-depth/mindfulness-exercises/art-20046356
    furhat.say("Lie on your back with your legs extended and arms at your sides, palms facing up.")
    furhat.say("Focus your attention slowly and deliberately on each part of your body, in order, from toe to head or head to toe. Be aware of any sensations, emotions or thoughts associated with each part of your body.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

def five_senses_exercise(furhat, lock, queue):
    #https://www.verywellhealth.com/mindfulness-exercises-5204406
    furhat.say("Notice five things you can see.")
    time.sleep(5)
    furhat.say("Notice four things you can feel.")
    time.sleep(5)
    furhat.say("Notice three things you can hear.")
    time.sleep(5)
    furhat.say("Notice two things you can smell.")
    time.sleep(5)
    furhat.say("Notice one thing you can taste.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return


def walking_meditation(furhat, lock, queue):
    #https://www.mayoclinic.org/healthy-lifestyle/consumer-health/in-depth/mindfulness-exercises/art-20046356
    furhat.say("Find a quiet place 10 to 20 feet in length, and begin to walk slowly. "
               "Focus on the experience of walking, being aware of the sensations of standing and the subtle movements that keep your balance. When you reach the end of your path, turn and continue walking, maintaining awareness of your sensations.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

def gratitude_list(furhat, lock, queue):
    #https://www.healthline.com/health/mind-body/mindfulness-activities#for-adults
    furhat.say("Creating a gratitude list may help improve well-being and promoteTrusted Source positivity by helping you focus on the things that you’re grateful for.")
    furhat.say("Try adding 3-5 items to your list each day and build it into your daily schedule to stay consistent.")
    furhat.say("You can write your gratitude list first thing in the morning to get your day off to a great start or list a few things that you’re grateful for before winding down for bed.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock)
    if stopped:
        return

