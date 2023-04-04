import wave
import pyaudio
import numpy as np
import pyttsx3 as tts
import speech_recognition as sr

class Voice():
    def __init__(self, update_plot_bars) -> None:
        self.CHUNK = 1024
        self.MAX_AMP = 13000
        self.update_plot_bars = update_plot_bars
        self.voice_engine = tts.init()
        self.voice_recognizer = sr.Recognizer()
        self.voice_engine.setProperty('voice', self.voice_engine.getProperty('voices')[2].id)

    def get_text_from_mic(self) -> str | bool:
        try:
            with sr.Microphone() as mic:
                print("Listening...")
                # self.voice_recognizer.adjust_for_ambient_noise(
                #     source=mic, duration=.3)
                audio = self.voice_recognizer.listen(
                    source=mic, phrase_time_limit=4)
                my_text = self.voice_recognizer.recognize_google(
                    audio_data=audio, language="pt-BR", show_all=True)

                if type(my_text) == dict:
                    my_text = my_text['alternative'][0]['transcript'].lower()
                    print("Jarvis listened: ", my_text)
                else:
                    print("Jarvis didn't listen to anything")
                    
                return my_text

        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            self.say("Talvez o senhor não esteja conectado na internet")
            return False

        except sr.UnknownValueError:
            print("Unknown error ocurred")
            self.say("Um erro desconhecido ocorreu senhor")
            return False

    def say(self, text) -> None:
        self.voice_engine.save_to_file(text, "jarvis.wav")
        self.voice_engine.runAndWait()
        
        with wave.open("jarvis.wav", 'rb') as wf:
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

            while len(frame := wf.readframes(self.CHUNK)):
                amplitude = np.frombuffer(buffer=frame, dtype=np.int16).tolist()
                self.update_plot_bars(amplitude)
                stream.write(frame)
                
            self.update_plot_bars(np.zeros(shape=(self.CHUNK), dtype=np.int16).tolist())
            stream.close()
            p.terminate()
            