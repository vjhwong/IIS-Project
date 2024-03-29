import numpy
from furhat_remote_api import FurhatRemoteAPI
import time
import threading
import password_manager
import furhat_emotions

# Controls the whole interaction system. It consists of the main conversation loop as well as conversation branches.
# Such as the different exercises the user can do.

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

ANONYM_NAME = "Anonym"
REPEAT_MESSAGE = "I couldn't catch that, let me repeat myself."
OTHER_OPTION = 'other option'
END = 'end'
STOP = 'STOP'
SKIP = '--SKIP--'
done_exercises = []
BACK = '--BACK--'

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


def identification(furhat):
    # Controls the whole identification process with the password_manager.py file.
    # It either creates new profile for the user, logs in the user or starts an anonymous mode

    furhat.gesture(body=furhat_emotions.HAPPY())
    answered = False
    name = ''
    while not answered:
        furhat.gesture(name="OpenEyes")

        furhat.say(text="You can skip the identification process and enter an anonymous mode.")
        time.sleep(2)
        furhat.say(text="Otherwise, do you already have a profile and identification?")
        time.sleep(2)
        result = furhat.listen()
        print("message was:" + result.message)
        if result.message == '':
            result = furhat.listen()
            print("message was:" + result.message)
        if result.message == '':
            continue
        identified = False
        furhat.gesture(body=furhat_emotions.reset_emotions())
        if "skip" in result.message or "anonymous" in result.message or "anonym" in result.message:
            return start_anonym_mode(furhat)

        if "yes" in result.message or "I do" in result.message or "identification" in result.message or "I have a profile" in result.message or "identify" in result.message:
            furhat.say(text="Please, identify yourself with a name and a password.")
            # TODO we could just keep name, but then if there were two Eves in a family and one would already use it, furhat would tell she uses it already which sounds like a gdpr problem
            time.sleep(2)
            while not identified:
                name, password = listen_to_name_and_password(furhat)
                if name == SKIP:
                    return start_anonym_mode(furhat)
                if name == BACK:
                    break
                if name is None:
                    furhat.say(text="I didn't get that, would you like to repeat it " \
                                    "or do you want to create a new profile?")
                    furhat.gesture(name="Thoughtful")
                    
                    time.sleep(2)
                    result = furhat.listen()
                    if "repeat" in result.message or "again" in result.message:
                        furhat.say(text="Please, identify yourself with a name and a password.")
                        time.sleep(2)
                    elif "new profile" in result.message or "create" in result.message:
                        break
                    continue
                if is_name_and_password_valid(name,password):
                    identified = True
                    furhat.gesture(name="BigSmile")
                    furhat.say(text="Hello " + name + ". Welcome back! I'm happy to see you.")
                    return name
                else:
                    furhat.say(text="I'm sorry, I don’t seem to know " + name + " with that password, would you like to repeat it " \
                                    "or do you want to create a new profile?")
                    furhat.gesture(name="Shake")
                    
                    time.sleep(2)
                    result = furhat.listen()
                    if "repeat" in result.message or "again" in result.message:
                        furhat.say(text="Please, identify yourself with a name and a password.")
                        time.sleep(2)

            if not identified:
                return create_new_profile(furhat)
        elif "new profile" in result.message or "no" in result.message or "don't have a profile" in result.message:
            return  create_new_profile(furhat)
        else:
            if furhat_should_repeat_itself(result.message):
                time.sleep(2)
                continue
            else:
                furhat.say(text = REPEAT_MESSAGE)


    return name

def start_anonym_mode(furhat):
    furhat.say(text="You decided to enter an anonymous mode. Welcome.")
    furhat.gesture(name="Smile")

    return ANONYM_NAME

def create_new_profile(furhat):
    # creates a new profile for the user with selected password and not already used name
    furhat.say(text="Let's create a new profile for you. "
                    "Tell me your name and password you want to use for your identification. "
                    "Say it slow in order name and password")
    furhat.gesture(name="Smile")
    
    time.sleep(5)

    identified = False

    while not identified:
        name, password = listen_to_name_and_password(furhat)
        if name == SKIP:
            return start_anonym_mode(furhat)
        if name == BACK:
            break
        if name is None:
            furhat.say(text="I didn't get that, can you repeat it?")
            furhat.gesture(name="BrowRaise")

            time.sleep(2)
            continue

        if name == ANONYM_NAME:
            furhat.say(text="You can't enter this name, pick a different one.")
            furhat.gesture(name="Shake")
            time.sleep(2)
            continue

        if password_manager.is_username_already_stored(name):
            furhat.say(
                text="A profile with this name already exists. Pick another version of your name that will be used for your identification."
                     "Don't forget to remember it.")
            time.sleep(2)
            furhat.say(text="Tell me your name and password you want to use for your identification. "
                            "Say it slow in order name and password")
            furhat.gesture(name="Thoughtful")
            time.sleep(2)
            continue

        furhat.say(text="I understood " + name + " with " + password + " as a password. Is this correct?")
        time.sleep(2)
        result = furhat.listen()
        if ("yes" in result.message or "correct" in result.message) and "not correct" not in result.message and "isn't correct" not in result.message:
            save_name_and_password(name, password)
            furhat.say(text="Hello " + name + ", your new profile has been created! I am excited to start our new journey.")
            time.sleep(2)
            furhat.gesture(name="BigSmile")
            identified = True
            return name
        else:
            furhat.say(text="You didn't say it was correct. "
                            "Could you please tell me your name and password you want to use for your identification again?"
                            "Say it slow in order name and password.")
            furhat.gesture(name="Shake")
            time.sleep(3)

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
    if "skip" in result.message:
        return SKIP
    if "back" in result.message:
        return BACK
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
    password_manager.save_username_and_password(name, password)

def is_name_and_password_valid(name,password):
    return password_manager.validate_password(name, password)

def run_conversation_loop(name, furhat, queue):
    # The main conversation loop that starts exercise based on user's emotion
    # and suggest different exercise after the last one ended.
    lock = threading.Lock()
    conversation_ended = False
    first_interaction = True

    while not conversation_ended:
        em = get_an_emotion(queue, lock)
        if len(em) != 0 and (em[0] is not None or em[0] != ''):
            if first_interaction:
                reply = START_EMOTION_REPLY.get(em[0])

                time.sleep(2)
                furhat.say(text=reply)
                react_based_on_emotion(furhat, em[0])
                result = furhat.listen()
                time.sleep(2)
                first_interaction = False
                was_happy = start_interaction_based_on_emotion(name, furhat, queue, em[0], lock)
                if not was_happy:
                    session_should_end = offer_option_and_end_session_if_user_not_happy(name, furhat, queue, lock)
                    if session_should_end:
                        break
                    furhat.gesture(name="Smile")
            else:
                furhat.say(text="Is there anything else I can do for you?")

                wants_exercise_by_emotion = user_wants_to_do_exercise_based_on_emotion(em[0], done_exercises)
                if wants_exercise_by_emotion:
                    was_happy = start_interaction_based_on_emotion(name, furhat, queue, em[0], lock)
                    continue

                furhat.say(text="Do you want me to list you options of other exercises?")
                furhat.gesture(name="Smile")
                time.sleep(2)
                result = furhat.listen()
                result = result.message

                if "yes" in result or other_options_word_in_response(result):
                    session_should_end = offer_option_and_end_session_if_user_not_happy(name, furhat, queue, lock)
                    if session_should_end:
                        break
                elif "end" in result or "stop" in result or "leave" in result:
                    break

        time.sleep(5)
    furhat.gesture(name="BigSmile")
    furhat.gesture(name="CloseEyes")
    end_session(furhat, queue)
    return

def react_based_on_emotion(furhat, emotion):
    match emotion:
        case 'fear':
            furhat.gesture(name="Thoughtful")
        case 'surprise':
            furhat.gesture(name="Thoughtful")
        case 'angry':
            furhat.gesture(name="Thoughtful")
        case 'happy':
            furhat.gesture(name="Smile")
        case 'sad':
            furhat.gesture(name="Thoughtful")
        case 'neutral':
            furhat.gesture(name="Smile")
        case 'disgust':
            furhat.gesture(name="Thoughtful")

def ask_if_offer_option_or_end(furhat, queue):
    answered = False
    while not answered:
        furhat.say(text="Do you want to see other options? Or do you want to end this session?")
        furhat.gesture(name="Smile")
        time.sleep(2)
        result = furhat.listen()
        stop_in_response = was_stop_word_in_response(result.message)
        if stop_in_response:
            end_session(furhat, queue)
            answered = True
            return END
        elif other_options_word_in_response(result.message):
            answered = True
            return OTHER_OPTION
        else:
            furhat.say(text=REPEAT_MESSAGE)
            time.sleep(2)

def end_session(furhat, queue):
    # TODO save user happiness and stats so that assistent can react to it the next session
    furhat.say(text="You decided to end this session. Thank you for spending time with me today. I'll see you next time. Have a great day!")
    furhat.gesture(name="CloseEyes")
    queue.queue.clear()
    queue.put(STOP)

def offer_option_and_end_session_if_user_not_happy(name, furhat, queue, lock):
    session_should_end = False
    while not session_should_end:
        was_happy = offer_options(name, furhat, queue, lock)

        if not was_happy:
            result = ask_if_offer_option_or_end(furhat, queue)
            if result == END:
                return True
            else:
                continue
        else:
            return False


def other_options_word_in_response(response):
    if "list" in response or "options" in response or "different" in response:
        return True
    return False

def user_wants_to_do_exercise_based_on_emotion(emotion, done_exercises):
    match emotion:
        case 'fear':
            if mindfulness_exercise.__name__ in done_exercises:
                return False
            else:
                furhat.say(text="I would recommend mindfulness exercise for happiness. Do you want to start that?")
        case 'surprise':
            if mindfulness_exercise.__name__ in done_exercises:
                return False
            else:
                furhat.say(text="I would recommend mindfulness exercise for happiness. Do you want to start that?")
        case 'angry':
            if breathing_exercice.__name__ in done_exercises:
                return False
            else:
                furhat.say(text="I would recommend breathing exercise. Do you want to start that?")
        case 'happy':
            if meditation_for_happiness.__name__ in done_exercises:
                return False
            else:
                furhat.say(text="I would recommend meditation for happiness. Do you want to start that?")
        case 'sad':
            if breathing_exercice.__name__ in done_exercises:
                return False
            else:
                furhat.say(text="I would recommend breathing exercise for happiness. Do you want to start that?")
        case 'neutral':
            if mindfulness_exercise.__name__ in done_exercises:
                return False
            else:
                furhat.say(text="I would recommend mindfulness exercise for happiness. Do you want to start that?")
        case 'disgust':
            if mindfulness_exercise.__name__ in done_exercises:
                return False
            else:
                furhat.say(text="I would recommend mindfulness exercise for happiness. Do you want to start that?")

    time.sleep(2)
    result = furhat.listen()
    result = result.message
    if "don't start" in result or "stop" in result or "no" in result:
        return False
    else:
        return True


def start_interaction_based_on_emotion(name, furhat, queue, emotion, lock):
    furhat.say(text="I will pick an exercise specifically selected for you right now.")
    furhat.gesture(body=furhat_emotions.HAPPY())
    time.sleep(5)
    furhat.gesture(body=furhat_emotions.reset_emotions())
    match emotion:
        case 'fear':
            return mindfulness_exercise(name, furhat, lock, queue)
        case 'surprise':
            return mindfulness_exercise(name, furhat, lock, queue)
        case 'angry':
            return breathing_exercice(name, furhat, lock, queue)
        case 'happy':
            return meditation_for_happiness(name, furhat, lock, queue)
        case 'sad':
            was_happy = say_comforting_story(furhat, lock, queue)
            if was_happy:
                return breathing_exercice(name, furhat, lock, queue)
            else:
                return False
        case 'neutral':
            return mindfulness_exercise(name, furhat, lock, queue)
        case 'disgust':
            return mindfulness_exercise(name, furhat, lock, queue)

def offer_options(name, furhat, queue, lock):
    # Offers user all the different exercises
    picked_exercise = False
    furhat.gesture(body=furhat_emotions.SURPRISE(2))
    while not picked_exercise:
        furhat.say(text="I caught that you want to try something different. We can do: ")
        time.sleep(2)
        furhat.say(text="breathing exercise, ")
        time.sleep(2)
        furhat.say(text="meditation for happiness, ")
        time.sleep(2)
        furhat.say(text="we can just talk, I can listen to what's on your mind and say few comforting words,")
        time.sleep(2)
        furhat.say(text="mindfulness exercises, I can list them if you'd like. ")
        time.sleep(2)
        furhat.say(text="So, what will it be? If you'd like to leave, you can just tell me to stop.")
        furhat.gesture(body=furhat_emotions.HAPPY())
        time.sleep(10)
        # TODO tell more about each
        answer = furhat.listen()
        result = answer.message
        furhat.gesture(body=furhat_emotions.reset_emotions())
        if "first" in result or "breathing exercise" in result:
            picked_exercise = True
            #furhat.say(text="Do you want to know more or start or try something different?")
            #if "option" in result or "choice" in result or "different" in result:
            #    continue
            #if "more" in result:
            #    # TODO explain breathing exercise
            #    pass
            # leave option is done outside the if block
            return breathing_exercice(name, furhat, queue, lock)
        elif "second" in result or "meditation for happiness" in result or "meditation" in result or "happiness" in result:
            picked_exercise = True
            #furhat.say(text="Do you want to know more or start or try something different?")
            #if "option" in result or "choice" in result or "different" in result:
            #    continue
            #if "more" in result:
            #    # TODO explain meditation
            #    pass
            # leave option is done outside the if block
            return meditation_for_happiness(name, furhat, lock, queue)
        elif "third" in result or "talk" in result or "listen" in result or "comforting" in result:
            picked_exercise = True
            #furhat.say(text="Do you want to know more or start or try something different?")
            #if "option" in result or "choice" in result or "different" in result:
            #    continue
            #if "more" in result:
            #    # TODO explain listening and comforting
            #    pass
            return say_comforting_story(furhat, lock, queue)
        elif "last" in result or "fifth" in result or "mindfulness exercise" in result or "list" in result:
            picked_exercise = True
            #furhat.say(text="Do you want to know more or start or try something different?")
            #if "option" in result or "choice" in result or "different" in result:
            #    continue
            #if "more" in result:
            #    # TODO explain mindfulness exercise
            #    pass
            return list_mindfulness_exercise_and_let_pick(furhat, lock, queue)

        elif not was_stop_word_in_response(result):
            furhat.say(text="I'm sorry, I didn't catch that. Let me repeat the options again.")
            time.sleep(2)
            continue

        if was_stop_word_in_response(result):
            return False

        time.sleep(5)

def list_mindfulness_exercise_and_let_pick(furhat, lock, queue):
    # Let user pick a specific mindfulness exercise
    picked_option = False
    while not picked_option:
        furhat.say(text="There are multiple exercises you can try. "
                        "mindful breathing, body scan, five senses exercise, walking meditation, observe with eyes closed, and gratitude list. "
                        "Which one do you want to try?")
        furhat.gesture(body=furhat_emotions.HAPPY())
        time.sleep(15)
        result = furhat.listen()
        result = result.message
        print("list mindfulness exercises message: " + result)
        furhat.gesture(body=furhat_emotions.reset_emotions())
        if "again" in result or "once more" in result or "repeat" in result:
            continue
        elif "stop" in result or "end" in result:
            return False
        elif "other options" in result:
            return False
        elif "first" in result or "mindful breathing" in result:
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
        elif "fifth" in result or "observe" in result or "eyes closed" in result:
            picked_option = True
            return observe_with_eyes_closed(furhat, lock, queue)
        elif "last" in result or "sixth" in result or "gratitude list" in result:
            picked_option = True
            return gratitude_list(furhat, lock, queue)
        else:
            furhat.say(text="I'm sorry, I didn't catch that. Let me repeat the options again.")
        time.sleep(5)

def get_an_emotion(queue, lock):
    # Reads last emotion from a queue.
    # The detect faces thread has an access to this queue and puts the predicted emotions there.
    
    with lock:
        em = queue.get()
    # em = predict_emotion(aus, model)
    print("controller emotion " + em, flush=True)

    return em

def is_happy_by_emotion(queue, lock, furhat): #TODO add original emotion so that if person is angry at the beginning, it won't stop like this
    em = get_an_emotion(queue, lock)
    if len(em) != 0 and (em[0] is not None or em[0] != ''):
        if (em[0] == 'angry' or em[0] == 'disgust'):
            furhat.say(text="I see you don't want to do this.")
            furhat.gesture(body='Shake')

            return user_wants_to_try_something_different(furhat)
    return True

def user_wants_to_try_something_different(furhat):
    furhat.say(text="Do you want to try something different?")
    time.sleep(2)
    result = furhat.listen()
    if "yes" in result.message or "stop" in result.message or "different" in result.message:
        furhat.say(text="Let's try something different then!")
        return True
    else:
        furhat.say(text="Let's continue then!")
        return False

def stopped_if_user_wants_to_stop(queue, lock, furhat): # TODO what if the user wants to stop the whole session?
    if does_user_want_to_stop(queue, lock, furhat):
        return user_wants_to_try_something_different(furhat)


def does_user_want_to_stop(queue, lock, furhat):
    # See if user is angry or disgusted, in that case, they're clearly not happy with the exercise picked and pick another one
    # Or, listen if user said stop in their response
    if listen_for_stop_in_response(furhat):
        return True
    if not is_happy_by_emotion(queue, lock, furhat):
        return True
    return False

def listen_for_stop_in_response(furhat):
    result = furhat.listen()
    if was_stop_word_in_response(result.message):
        furhat.say(text="I heard stop. Do you want to stop?")
        furhat.gesture(body=furhat_emotions.SAD(2))

        result = furhat.listen()
        if "yes" in result.message:
            return True
    return False

def was_stop_word_in_response(response):
    if "stop" in response or "end" in response or "leave" in response:
        return True
    return False

def breathing_exercice(name, furhat, queue, lock):
    #https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/
    furhat.say(text="Here's a simple breathing exercise. Can we start? ")
    time.sleep(2)
    result = furhat.listen()
    if "yes" in result.message:
        furhat.say(text="Let's start. If you wish to stop at any time, you can just say so.")
        time.sleep(2)
    elif "how long" in result.message:
        furhat.say(text="This breathing exercise takes just a few minutes.")
    elif "other choice" in result.message or "something different" in result.message:
        return False
    elif "no" in result.message:
        furhat.say(text="I caught that you don't want to do this.")
        return False
    elif was_stop_word_in_response(result.message):
        return False

    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="You can do it standing up, sitting in a chair that supports your back, or lying on a bed or yoga mat on the floor.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(
        text="Make yourself as comfortable as you can. If you can, loosen any clothes that restrict your breathing.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(
        text="If you're lying down, place your arms a little bit away from your sides, with the palms up. Let your legs be straight, "
             "or bend your knees so your feet are flat on the floor.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(
        text="If you're sitting, place your arms on the chair arms.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(
        text="If you're sitting or standing, place both feet flat on the ground. Whatever position you're in, "
             "place your feet roughly hip-width apart.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(
        text="Let your breath flow as deep down into your belly as is comfortable, without forcing it.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(
        text="Try breathing in through your nose and out through your mouth.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(
        text="Breathe in gently and regularly. Some people find it helpful to count steadily from 1 to 5. You may not be able to reach 5 at first.")

    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(
        text="Then let it flow out gently, counting from 1 to 5 again, if you find this helpful.")
    time.sleep(1)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(text="But let's try it together. Breath in.")

    furhat.say(text="One")
    time.sleep(1)
    furhat.say(text="Two")
    time.sleep(1)
    furhat.say(text="Three")
    time.sleep(1)
    furhat.say(text="Four")
    time.sleep(1)
    furhat.say(text="Five. Now breath out.")
    furhat.say(text="One")
    time.sleep(1)
    furhat.say(text="Two")
    time.sleep(1)
    furhat.say(text="Three")
    time.sleep(1)
    furhat.say(text="Four")
    time.sleep(1)
    furhat.say(text="Five")

    furhat.say(
        text="Now, repeat this for at least five minutes. I will be notifying you about the time, after each minute passes")

    iteration = 1
    for i in range(10): #there is no timeout for furhat in this api
        result = furhat.listen()
        if result != '':
            furhat.say(text="Do you want to stop?")
            result = furhat.listen()
            if "yes" in result.message:
                break
        if iteration == 1:
            furhat.say(
                text= str(iteration) + " minute has passed. Let's keep doing this, you're doing great!")
        else:
            furhat.say(
                text=str(iteration) + " minutes has passed. Let's keep doing this, you're doing great!")
        iteration += 1
        time.sleep(6)

    furhat.say(
        text="You've finished this breathing exercise. You will get the most benefit if you do it regularly, as part of your daily routine.")
    furhat.gesture(body=furhat_emotions.HAPPY())

    return did_session_help(furhat, breathing_exercice.__name__)

def did_session_help(furhat, session_name):
    done_exercises.append(session_name)
    furhat.say(text="Thank you for spending time with me. Did this session help?")
    time.sleep(2)
    result = furhat.listen()
    if "yes" in result.message:
        furhat.say(text="I'm glad this helped. Hope to see you tomorrow.")
        furhat.gesture(name="BigSmile")
    else:
        return False
    return True

def say_comforting_story(furhat, lock, queue):
    furhat.say(text="To understand you better, what happened? Is this work related or school related? Or is it related to relationships?")
    furhat.gesture(name="Thoughtful")
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
                furhat.say(text="You can try some of my relaxing meditations or breathing exercises.")
                time.sleep(2)
            elif result != "":
                furhat.say(
                    "I understand. That is a difficult situation. But remember, challenges are what make life interesting"
                    "and overcoming them is what makes life meaningful.")
                time.sleep(2)
                result = furhat.listen()
        if "school" in result or "uni" in result or "university" or "college" in result or "teacher" in result or "classmate" in result:
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
                furhat.say(text="You can try some of my relaxing meditations or breathing exercises.")
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
        elif was_stop_word_in_response(result):
            return False
        else:
            furhat.say(
                "I didn't catch that. Can you repeat it, please?")

    return did_session_help(furhat, say_comforting_story.__name__)

def meditation_for_happiness(name, furhat, lock, queue):
    #https://jackcanfield.com/blog/happiness-meditation/
    furhat.say(text="Here's a simple guided meditation for happiness. Can we start? ")
    time.sleep(2)
    result = furhat.listen()
    if "yes" in result.message:
        furhat.say(text="Let's start. If you wish to stop at any time, you can just say so.")
        furhat.gesture(body=furhat_emotions.HAPPY())
        time.sleep(2)
    if "how long" in result.message:
        furhat.say(text="This meditation is for 10 minutes.")
    if "other choice" in result.message or "something different" in result.message:
        #furhat.say(text="Do you want to try something different?")
        return False
    if "no" in result.message:
        return False

    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="Sit for a moment and take a few long inhalations and exhalations. Focus on the breathing.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(text="Breath in slowly and breath out slowly.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(text="CLear your mind. If you find your thoughts shifting from the breathing, gently release that thought and concentrate on breathing.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(text="Think of your thoughts as train cars passing through the station. You’re on the platform, watching them go past.")
    time.sleep(10)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="Your mind should be quiet now. Let's thank to what you're experiencing.")
    time.sleep(2)
    furhat.say(text="Give thanks to your mind, which allows you to think of all your thoughts. ")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(text="Be grateful for your eyes, that allow you to see the world’s beauty. "
               "Give thanks to your ears that allow you to hear the world’s music, and then to your mouth "
               "that allows you to taste the world’s deliciousness in all its myriad forms.")
    time.sleep(5)
    furhat.say(text="Be grateful for your arms and your hands and all they allow you to do.")
    time.sleep(2)
    furhat.say(text="Such as holding a child, reaching out and grabbing something to you, throwing a ball or a pillow, \
               catching a ball or your falling child, writing a book, typing a report, driving a car, "
               "playing a musical instrument, creating a piece of art, cooking a meal, or hugging a loved one, "
               "or making love.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(text="Be grateful for your lungs, for allowing you to breathe, and for your throat, for allowing you to speak and sing. "
               "And be grateful for your legs and feet, for making it possible for you to walk, run, jump, and dance.")
    time.sleep(10)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="Be grateful for the chair you’re sitting on, and the people who put their time and effort into making that chair. "
               "Be grateful for the money that allowed you to buy that chair, or the person who gave it to you.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False
    furhat.say(text="Be grateful for the coffee cup beside you, and the delicious coffee it used to hold "
               "that’s now flowing through your veins, making you feel more awake and alert.")
    time.sleep(2)
    furhat.say(text="Be grateful for the clothes that you’re wearing, and the person who made those clothes, "
               "and the job that gave you the money you needed to buy them.")
    time.sleep(2)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="Be grateful for your home, and your family and your friends. "
               "Be grateful for the people who make your life better or easier in some way—"
               "like the people at the grocery store, the gas station, the coffee shops, and the restaurants—the garbage men, "
               "the taxi drivers and Uber drivers, the weathermen and women, the doctors, nurses, healers and holistic practitioners.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="Be grateful for the city and the country you live in, and the freedoms and rights that are available to you. "
               "Be grateful for the natural world around you—the birds that you hear out the window, the flowers and the trees, "
               "the parks and the bodies of water, and the fish that swim the ocean. ")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="Expand your gratitude to whatever you can think of. You can even feel gratitude for the planet, the solar system, the stars, and even for life itself!")
    furhat.say(text="Gently let your mind drift from topic to topic, while consciously practicing gratitude for everything that occurs to you.")
    furhat.say(text="Try to maintain this state for about 5 minutes if you can.")
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    iteration = 1
    for i in range(10):  # there is no timeout for furhat in this api
        result = furhat.listen()
        if result != '':
            furhat.say(text="Do you want to stop?")
            result = furhat.listen()
            if "yes" in result.message:
                break
        iteration += 1
        time.sleep(6)

    furhat.say(text="Open your eyes.")
    time.sleep(1)
    furhat.say(text="Now, take a moment to acknowledge the joy that comes with showing this kind of gratitude.")
    time.sleep(1)
    furhat.say(text="It is important to pause and recognize that small, incremental changes in your daily life can build up "
               "and make larger improvements in your mental health.")
    time.sleep(2)
    furhat.say(text="This simple meditation can have a huge impact on your mindset and your vibration. "
               "If you practice this exercise tomorrow as well, you will find it so much easier to experience more joy "
               "and happiness in your life.")
    time.sleep(2)

    return did_session_help(furhat, meditation_for_happiness.__name__)

def mindfulness_exercise(name, furhat, lock, queue):
    furhat.say(text="Let me list all mindfulness exercises for you and then you can pick one")
    furhat.gesture(name='Smile')
    was_happy = list_mindfulness_exercise_and_let_pick(furhat, lock, queue)
    if was_happy:
        return did_session_help(furhat, mindfulness_exercise.__name__)
    else:
        return False

def mindful_breathing(furhat, lock, queue):
    furhat.say(text="Let's start the mindful breathing exercise")
    time.sleep(2)
    # https://www.verywellhealth.com/mindfulness-exercises-5204406 and https://www.healthline.com/health/box-breathing#hold-your-breath

    furhat.say(text="This technique can be beneficial to anyone, especially those who want to meditate or reduce stress.")
    time.sleep(2)
    furhat.say(text=
        "Make sure that you’re seated upright in a comfortable chair with your feet flat on the floor. Try to be in a stress-free, quiet environment where you can focus on your breathing.")
    time.sleep(2)
    furhat.say(text="Keeping your hands relaxed in your lap with your palms facing up, focus on your posture.")
    time.sleep(5)
    stopped = stopped_if_user_wants_to_stop(queue, lock, furhat)
    if stopped:
        return False

    furhat.say(text="Breathe in through your nose for a count of 4. Feel the air fill your lungs, one section at a time, until your lungs are completely full and the air moves into your abdomen.")
    time.sleep(4)
    furhat.say(text="Now hold for another 4 seconds")
    time.sleep(4)
    furhat.say(text="Exhale through your mouth for a count of 4. Be conscious of the feeling of the air leaving your lungs.")
    time.sleep(4)
    furhat.say(text="Now hold for another 4 seconds")
    time.sleep(4)
    furhat.say(text="Repeat until you want to stop.")
    time.sleep(5)

    return did_session_help(furhat, mindful_breathing.__name__)

def body_scan(furhat, lock, queue):
    furhat.say(text="Let's start the body scan exercise")
    furhat.gesture(body=furhat_emotions.HAPPY())
    time.sleep(2)
    #https://www.mayoclinic.org/healthy-lifestyle/consumer-health/in-depth/mindfulness-exercises/art-20046356
    furhat.say(text="Lie on your back with your legs extended and arms at your sides, palms facing up.")
    furhat.say(text="Focus your attention slowly and deliberately on each part of your body, in order, from toe to head or head to toe. Be aware of any sensations, emotions or thoughts associated with each part of your body.")
    time.sleep(5)

    return did_session_help(furhat, body_scan.__name__)

def five_senses_exercise(furhat, lock, queue):
    furhat.say(text="Let's start the five senses exercise exercise")
    time.sleep(2)
    #https://www.verywellhealth.com/mindfulness-exercises-5204406
    furhat.say(text="Notice five things you can see.")
    time.sleep(5)
    furhat.say(text="Notice four things you can feel.")
    time.sleep(5)
    furhat.say(text="Notice three things you can hear.")
    time.sleep(5)
    furhat.say(text="Notice two things you can smell.")
    time.sleep(5)
    furhat.say(text="Notice one thing you can taste.")
    time.sleep(5)

    return did_session_help(furhat, five_senses_exercise.__name__)


def walking_meditation(furhat, lock, queue):
    furhat.say(text="Let's start the owalking meditation exercise")
    time.sleep(2)
    #https://www.mayoclinic.org/healthy-lifestyle/consumer-health/in-depth/mindfulness-exercises/art-20046356
    furhat.say(text="Find a quiet place 10 to 20 feet in length, and begin to walk slowly. "
               "Focus on the experience of walking, being aware of the sensations of standing and the subtle movements that keep your balance. When you reach the end of your path, turn and continue walking, maintaining awareness of your sensations.")
    time.sleep(10)

    return did_session_help(furhat, walking_meditation.__name__)

def gratitude_list(furhat, lock, queue):
    #https://www.healthline.com/health/mind-body/mindfulness-activities#for-adults
    furhat.say(text="Creating a gratitude list may help improve well-being and promoteTrusted Source positivity by helping you focus on the things that you’re grateful for.")
    time.sleep(1)
    furhat.say(text="Try adding 3-5 items to your list each day and build it into your daily schedule to stay consistent.")
    time.sleep(1)
    furhat.say(text="You can write your gratitude list first thing in the morning to get your day off to a great start or list a few things that you’re grateful for before winding down for bed.")
    time.sleep(5)

    return did_session_help(furhat, gratitude_list.__name__)

def observe_with_eyes_closed(furhat, lock, queue):
    furhat.say(text = "Let's start the observe with eyes closed exercise")
    time.sleep(2)
    #https://www.fearlessculture.design/blog-posts/21-simple-mindfulness-exercises-to-improve-your-focus
    furhat.say(text="Sometimes, the best way to remove a distraction is to stop seeing it.")
    time.sleep(2)
    furhat.say(text="This exercise is ideal to practice in public space.")
    time.sleep(2)
    furhat.say(text="Now, close your eyes.")
    time.sleep(2)
    furhat.say(text="Take a deep breath and relax.")
    time.sleep(2)
    furhat.say(text="Focus on what's going on around you. First, pay attention to the sounds that are closer to you.")
    time.sleep(2)
    furhat.say(text="What do you hear?")
    time.sleep(15)
    furhat.say(text="Little by little, start focusing on the sounds that are farther away.")
    time.sleep(15)
    furhat.say(text="Now, pay attention to what’s going on right next to you. What sounds do you hear? Can you hear voices? What are they saying?")
    time.sleep(15)
    furhat.say(text="Now repeat the same routine with the more distant noises, sounds, and voices. Remember that you are trying to understand, not to analyze, what’s happening.")
    time.sleep(15)
    furhat.say(text="Whenever you're ready, open your eyes and tell me to stop.")

    interrupted = False
    while not interrupted:
        result = furhat.listen()
        if was_stop_word_in_response(result.message):
            interrupted = True
        time.sleep(1)

    return did_session_help(furhat, observe_with_eyes_closed.__name__)
