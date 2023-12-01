from furhat_remote_api import FurhatRemoteAPI
import detect_faces
import interactive_system
import time
import threading


if __name__ == "__main__":
    furhat = interactive_system.set_furhat()
    furhat.say(text="Hi there!")

    #interaction_thread = threading.Thread(target=interactive_system.furhat_interaction)
    #interaction_thread.start()

    detect_faces_thread = threading.Thread(target=detect_faces.create_video())
    detect_faces_thread.start()

    while True:
        emotion = detect_faces.detect_emotion()
        interactive_system.furhat_interaction(emotion)
        time.sleep(3)

