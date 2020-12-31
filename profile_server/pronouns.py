import random
from enum import Enum


class PronounOptions(Enum):
    FEMALE = 'לשון נקבה'
    MALE = 'לשון זכר'
    NEUTRAL = 'לשון ניטרלית'
    MIXED = 'לשון מעורבת'


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
    'teach': WordOptions('מלמד', 'מלמדת', 'מלמד.ת'),
    'professional': WordOptions('מקצועי', 'מקצועית', 'מקצועי.ת'),
    'mentor': WordOptions('חונך', 'חונכת', 'חונכ.ת'),
    'sure': WordOptions('בטוח', 'בטוחה', 'בטוח.ה'),
    'click': WordOptions('לחץ', 'לחצי', 'לחצ.י'),
    'send': WordOptions('שלח', 'שלחי', 'שלח.י'),
    'enter': WordOptions('הכנס', 'הכניסי', 'הכנס.י'),
    'look': WordOptions('חפש', 'חפשי', 'חפש.י'),
    'to_you': WordOptions('אליך', 'אלייך', 'אלייך'),
    'choose': WordOptions('בחר', 'בחרי', 'בחר.י'),
    'you_can': WordOptions('תוכל', 'תוכלי', 'תוכל.י'),
    'ignore': WordOptions('התעלם', 'התעלמי', 'התעלמ.י'),
    'will_want': WordOptions('תרצה', 'תרצי', 'תרצ.י'),
}
