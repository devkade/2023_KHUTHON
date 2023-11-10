import speech_recognition as sr
import threading
import queue
import keyboard


class KeyboardThread(threading.Thread):
    def __init__(self, flag):
        threading.Thread.__init__(self)
        self.flag = flag
        
    def run(self):
        while True:
            if keyboard.is_pressed('q'):
                self.flag.set()
                break

# Multi-Thread_01 controling input audio
class SpeechToTextThread(threading.Thread):
    def __init__(self, audio_queue, flag, recognizer):
        threading.Thread.__init__(self)
        self.audio_queue = audio_queue
        self.flag = flag
        self.recognizer = recognizer

    def run(self):
        
        
        while not self.flag.is_set() or not self.audio_queue.empty():
            try:
                # Get audio from the queue
                audio = self.audio_queue.get(block=True, timeout=1)
                text = self.recognizer.recognize_google_cloud(
                    audio,
                    credentials_json='CREDENTIALS.json', #Input the path of your google-cloud credential.json file
                    language='ko-KR',
                )
                print(f"Transcription: {text}")
            
            except queue.Empty:
                pass  # Queue is empty, no audio available
            except sr.UnknownValueError:
                print("I didn't understand your words...Come again Plz?")
                print()
                pass  # Ignore if the audio is not recognized
            except sr.RequestError as e:
                print(f"Google Cloud Speech-to-Text request failed: {e}")
                
            except KeyboardInterrupt:
                # Stop the speech-to-text thread when the program is interrupted
                print("Exiting Education...")
                break   
        
        print("Exiting Education...")

def main():
    audio_queue = queue.Queue()
    flag = threading.Event()
    
    recognizer = sr.Recognizer()
    
    speech_thread = SpeechToTextThread(audio_queue, flag, recognizer)
    flag_thread = KeyboardThread(flag)

        # Start the speech-to-text thread
    flag_thread.start()
    speech_thread.start()


    # Multi_Thread_Main requesting origin audio data to GOOGLE & printing configuration
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while not flag.is_set():
            try:
                print("I'm listening..Umm...")
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                audio_queue.put(audio)
                
            except sr.UnknownValueError:
                print("I didn't understand your words...Come again Plz?")
                print()
                pass  # Ignore if the audio is not recognized
            except sr.RequestError as e:
                print(f"Google Cloud Speech-to-Text request failed: {e}")
            
            except KeyboardInterrupt:
                print("Exiting Education...")
                break
    
    speech_thread.join()
                    
    
if __name__ == "__main__":
    main()