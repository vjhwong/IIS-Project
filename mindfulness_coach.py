from furhat_remote_api import FurhatRemoteAPI
import detect_faces
import interactive_system
import time
import threading
import sys
import queue
from joblib import load

end_time_seconds = 30
def get_emotion(furhat, queue, model, name):
    lock = threading.Lock()
    t_end = time.time() + end_time_seconds
    while time.time() < t_end:
        print("reading emotion", flush=True)
        sys.stdout.flush()
        with lock:
            em = queue.get()
        #em = predict_emotion(aus, model)
        print("controller emotion " + em, flush=True)
        print(list(queue.queue))
        if em is not None or em != '':
            interactive_system.furhat_interaction(em, furhat)
        time.sleep(4)


def start_furhat_and_get_a_name():
    furhat = interactive_system.set_furhat()
    name = interactive_system.start_furhat(furhat)
    return furhat, name

def predict_emotion(aus, model):
    emotion = model.predict(aus)
    return emotion

if __name__ == "__main__":
    queue = queue.Queue()

    model = load('svm_model.joblib')
    detect_faces_thread = threading.Thread(target=detect_faces.create_video, args = [queue, model])
    detect_faces_thread.start()

    furhat, name = start_furhat_and_get_a_name()
    furhat_interaction = threading.Thread(target=interactive_system.run_conversation_loop, args=[name, furhat, queue])
    time.sleep(3)
    furhat_interaction.start()

    detect_faces.stop()
    detect_faces_thread.join()
    furhat_interaction.join()

