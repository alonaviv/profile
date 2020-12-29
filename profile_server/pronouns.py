from enum import Enum
import random


class PronounOptions(Enum):
    MALE = 'לשון זכר'
    FEMALE = 'לשון נקבה'
    NEUTRAL = 'לשון ניטרלית'
    MIXED = 'לשון מעורבבת'


class WordOptions:
    def __init__(self, male_word, female_word, neutral_word):
        self.word_options = {
            PronounOptions.MALE: male_word,
            PronounOptions.FEMALE: female_word,
            PronounOptions.NEUTRAL: neutral_word
        }

    def get_matching_word(self, pronoun: PronounOptions):
        if pronoun is PronounOptions.MIXED:
            return random.choice([self.word_options[PronounOptions.MALE], self.word_options[PronounOptions.FEMALE]])

        else:
            return self.word_options[pronoun]


class PronounWordDictionary:
    def __init__(self, requested_pronoun: PronounOptions):
        self.pronoun_options_dict = pronoun_options_dict
        self.requested_pronoun = requested_pronoun

    def __getitem__(self, word: str):
        return pronoun_options_dict[word].get_matching_word(self.requested_pronoun)


# ======== Write in pronoun options here
pronoun_options_dict = {
    'you': WordOptions('אתה', 'את', 'את.ה'),
    'teach': WordOptions('מלמד', 'מלמדת', 'מלמד.ת')
}

