import AppOpener
import speech_recognition as sr
import webbrowser
import pywhatkit
from audio import Voice
import pickle
import spacy
from spacy.matcher import Matcher

class Jarvis():
    def __init__(self, update_plot_bars, bring_window_to_top, hide_window) -> None:
        self.bring_window_to_top = bring_window_to_top
        self.hide_window = hide_window
        self.voice = Voice(update_plot_bars)
        self.nlp = spacy.load("pt_core_news_md")
        self.nlu_model = pickle.load(open("./nlu_model/classification_model.pkl", "rb"))
        self.vectorizer = pickle.load(open("./nlu_model/vectorizer.pkl", "rb"))

        self.running = True
        self.app_names = AppOpener.give_appnames()
        self.patterns = {
            "open app": [
                [{"POS": "NOUN"}]
            ],
            "close app": [
                [{"POS": "NOUN"}]
            ],
            "turn mode": [
                [{"POS": "NOUN", "OP": "{1}"}]
            ],
            "search": [
                [{"IS_SENT_START": False}]
            ],
            "music": [
                [{"IS_SENT_START": False}]
                # [{"POS": "NOUN", "OP": "+"}, {"POS": "ADJ", "OP": "*"}, {"POS": "VERB", "OP": "*"}]
            ],
            "turn off": [
                [{}]
            ],
        }
        self.modes = {
            "jogo": "steam, discord, spotify",
            "programação": "vscode, chrome, spotify",
        }
        
    def start(self) -> None:
        print("[!] Jarvis is running")
        while (self.running):
            if self.wake(self.listen()):
                self.is_awake = True
                print("[!] Jarvis is awake!")
                self.speak("Diga senhor")

                command = self.listen()

                if command:
                    self.think(command)
                
                self.is_awake = False
                print("[!] Jarvis is sleeping...")
                
        print("[!] Jarvis has stopped")

    def wake(self, text: str | bool) -> bool:
        if type(text) == list:
            return False
        return True if "jarvis" in text else False

    def pre_process_text_for_prediction(self, doc):
        processed_text = " ".join([token.lemma_.lower() for token in doc])
        return self.vectorizer.transform([processed_text])

    def process_text_to_action(self, doc, mode):
        matcher = Matcher(self.nlp.vocab)
        pattern = self.patterns[mode]
        matcher.add(mode, pattern)
        return matcher(doc, as_spans=True)

    def speak(self, text: str) -> None:
        self.bring_window_to_top()
        self.voice.say(text)

    def listen(self) -> str | bool:
        return self.voice.get_text_from_mic()

    def think(self, text: str) -> None:
        doc = self.nlp(text)
        vec_to_predict = self.pre_process_text_for_prediction(doc)
        prediction = self.nlu_model.predict(vec_to_predict)[0]
        matches = self.process_text_to_action(doc, prediction)
        
        if prediction == "open app":
            self.open_close_programs(doc[len(doc) - 1].text, open=True)
        elif prediction == "close app":
            self.open_close_programs(doc[len(doc) - 1].text, open=False)
        elif prediction == "turn mode":
            self.turn_mode(matches[len(matches) - 1].text)
        elif prediction == "search":
            self.search(" ".join([token.text for token in matches]))
        elif prediction == "music":
            self.search(" ".join([token.text for token in matches]))
        elif prediction == "turn off":
            self.turn_off()
        else:
            self.speak("Acho que me confundi")

        self.hide_window()

            
    def open_close_programs(self, app_name, open=True):
        AppOpener.open(app_name, open_closest=True) if open else AppOpener.close(app_name, close_closest=True)

    def turn_mode(self, mode_name):
        if mode_name in self.modes.keys():
            AppOpener.open(self.modes[mode_name], open_closest=True)
            self.speak(f"Ativando modo {mode_name}")
        else:            
            self.speak("Esse modo não existe")
                
    def search(self, text):
        webbrowser.open_new_tab(f"https://www.google.com/search?q={text}")
        self.speak(f"Isso foi o que encontrei pesquisando {text}")

    def play_music(self, music_name):
        pywhatkit.playonyt(music_name)
        self.speak(f"Tocando {music_name} no Youtube")
        
    def turn_off(self):
        self.speak("Até mais senhor")
        self.running = False
