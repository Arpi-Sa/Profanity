import os
import re
import inflection


class ProfanityFilter:
    def __init__(self, **kwargs):

        # If defined, use this instead of _censor_list
        self._custom_censor_list = kwargs.get('custom_censor_list', [])

        # Words to be used in conjunction with _censor_list
        self._extra_censor_list = kwargs.get('extra_censor_list', [])

        # What to be censored -- should not be modified by user
        self._censor_list = []

        # What to censor the words with
        self._censor_char = "*"

        # Where to find the censored words
        self._BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self._words_file = os.path.join(self._BASE_DIR, 'data', 'bw.txt')

        self._load_words()

    def _load_words(self):
        with open(self._words_file, 'r') as f:
            self._censor_list = [line.strip() for line in f.readlines()]

    def define_words(self, word_list):
        self._custom_censor_list = word_list

    def append_words(self, word_list):
        self._extra_censor_list.extend(word_list)

    def set_censor(self, character):
        if isinstance(character, int):
            character = str(character)
        self._censor_char = character

    def has_bad_word(self, text):
        return self.censor(text) != text

    def get_custom_censor_list(self):
        return self._custom_censor_list

    def get_extra_censor_list(self):
        return self._extra_censor_list

    def get_profane_words(self):
        profane_words = []

        if self._custom_censor_list:
            profane_words = self._custom_censor_list.copy()
        else:
            profane_words = self._censor_list.copy()

        profane_words.extend(self._extra_censor_list)
        profane_words.extend([inflection.pluralize(word) for word in profane_words])
        profane_words = list(set(profane_words))

        return profane_words

    def restore_words(self):
        self._custom_censor_list = []
        self._extra_censor_list = []
        #self._load_words()
        #print("Hey" in self.get_profane_words())


    def censor(self, input_text):
        bad_words = self.get_profane_words()
        res = input_text

        for word in bad_words:
            word = r'\b%s\b' % word  # Apply word boundaries to the bad word
            regex = re.compile(word, re.IGNORECASE)
            res = regex.sub(self._censor_char * (len(word) - 4), res)

        return res


    def is_clean(self, input_text):
        return not self.has_bad_word(input_text)


    def is_profane(self, input_text):
        return self.has_bad_word(input_text)
