from furhat_remote_api import FurhatRemoteAPI
import detect_faces
import interactive_system
import time
import threading
import sys
import queue
from joblib import load

end_time_seconds = 30
def get_emotion(furhat, queue, model):
    lock = threading.Lock()
    t_end = time.time() + end_time_seconds
    while time.time() < t_end:
        print("reading emotion", flush=True)
        sys.stdout.flush()
        with lock:
            aus = queue.get()
        em = predict_emotion(aus, model)
        print("controller emotion " + em, flush=True)
        print(list(queue.queue))
        if em is not None or em != '':
            interactive_system.furhat_interaction(em, furhat)
        time.sleep(5)

def predict_emotion(aus, model):
    emotion = model.predict(aus)
    return emotion

if __name__ == "__main__":
    queue = queue.Queue()
    furhat = interactive_system.set_furhat()
    furhat.say(text="Hi there!")
    model = load('svm_model.joblib')

    get_emotion_thread = threading.Thread(target=get_emotion, args=[furhat, queue, model])
    detect_faces_thread = threading.Thread(target=detect_faces.create_video, args = [queue, model])

    detect_faces_thread.start()
    time.sleep(5)
    get_emotion_thread.start()

    detect_faces.stop()
    detect_faces_thread.join()
    get_emotion_thread.join()

