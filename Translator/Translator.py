from deep_translator import GoogleTranslator                       
import json
import plugins

# Load user settings
with open("../../../../User-Settings.json", "r", encoding='utf-8') as file:
    user_settings = json.load(file)

translator_settings = user_settings["Translation_API_Server"]["Google"]

class Main_Translator:
    def __init__(self):
        self.translator_ready_or_not = False
        self.can_change_language_or_not = True
        self.supported_languages_list = translator_settings["supported_languages_list"]
        self.input_language = self.supported_languages_list[ translator_settings["input_language"] ]
        self.output_language = self.supported_languages_list[ translator_settings["output_language"] ]
        self.translator = ""
        self.stop_translation = False

    def pause(self):
        self.stop_translation = True

    def resume(self):
        self.stop_translation = False

    def activate(self):
        self.translator = GoogleTranslator(source=self.input_language, target=self.output_language)
        self.translator_ready_or_not = True
        return self.translator_ready_or_not
    
    def translate(self, input_text):
        input_text = plugins.process_input_text(input_text)

        if (self.stop_translation == True):
            return "Translation is paused at the moment"
        else:
            translation_text = self.translator.translate(input_text)  
            translation_text = plugins.process_output_text(translation_text)
            return translation_text
    
    def translate_batch(self, list_of_text_input):
        if (self.stop_translation == True):
            return "Translation is paused at the moment"
        else:
            translation_list = []
            for text_input in list_of_text_input:
                translation = self.translate(text_input)
                translation_list.append(translation)
            return translation_list
    
    def check_if_language_available(self, language):
        if (self.supported_languages_list.get(language) == None):
            return False
        else: 
            return True
    
    def change_output_language(self, output_language):
        if (self.can_change_language_or_not == True):
            if (self.check_if_language_available(output_language) == True):
                self.output_language = output_language
                self.translator._target = self.supported_languages_list[output_language]
                return f"output language changed to {output_language}"
            else:
                return "sorry, translator doesn't have this language"
        else: 
            return "sorry, this translator can't change languages"

    def change_input_language(self, input_language):
        if (self.can_change_language_or_not == True):
            if (self.check_if_language_available(input_language) == True):
                self.input_language = input_language
                self.translator._source = self.supported_languages_list[input_language]
                return f"input language changed to {input_language}"
            else:
                return "sorry, translator doesn't have this language"
        else: 
            return "sorry, this translator can't change languages"
    
# google = Google_Translator()
# google.activate()
# print(google.translate("たまに閉じているものがあっても、中には何も入っていなかった。"))
# google.change_output_language("Vietnamese")
# print(google.translate("たまに閉じているものがあっても"))
# google.change_input_language("English")
# print(google.translate("Hello world"))



