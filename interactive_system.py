from furhat_remote_api import FurhatRemoteAPI

def main():
    furhat = FurhatRemoteAPI("localhost")
    voices = furhat.get_voices()
    furhat.set_voice(name='Matthew')


    furhat.say(text="Hi there!")

    

    

if __name__ == "__main__":
    main()