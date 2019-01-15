import os
import re
import pandas as pd
from Levenshtein import jaro_winkler
import inflection


class ProfanityFilter:
    def __init__(self, **kwargs):
        # What to be censored -- should not be modified by user
        self._censor_list = []

        # What to censor the words with
        self._censor_char = "*"

        # Where to find the censored words
        self._BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self._words_file = os.path.join(self._BASE_DIR, 'bw.txt')

        self._load_words()

    def _load_words(self):
        with open(self._words_file, 'r') as f:
            self._censor_list = [line.strip() for line in f.readlines()]

        self.df = pd.DataFrame(self._censor_list, columns=["Profane"])


    def __preprocess(self, text):
        return re.findall(r"\b\w\w*\b", text.lower())

    def _is_close(self, text, thresh=0.94):
        words = self.__preprocess(text)
        self.df["Scores"] = self.df["Profane"].apply(lambda x: max(jaro_winkler(w, x) for w in words))
        bword, score = self.df.sort_values("Scores", ascending=False).iloc[0].tolist()
        if score > thresh:
            return True
        return False


    def has_bad_word(self, text):
        return (self.censor(text) != text) or (self._is_close(text))


    def get_profane_words(self):
        profane_words = []
        profane_words = [w for w in self._censor_list]

        profane_words.extend([inflection.pluralize(word) for word in profane_words])
        profane_words = list(set(profane_words))

        return profane_words


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
