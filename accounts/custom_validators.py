from django.core.exceptions import ValidationError


class HebrewNumericPasswordValidator:
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError("על הסיסמא להכיל גם אותיות באנגלית וגם ספרות", code='password_entirely_numeric')

    def get_help_text(self):
        return 'על הסיסמא להכיל אותיות גם אותיות באנגלית וגם ספרות'


class HebrewMinimumLengthValidator:
    """
    Validate whether the password is of a minimum length.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(f"על הסיסמא להכיל לפחות {self.min_length} ספרות ",
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return f"על הסיסמא להכיל לפחות {self.min_length} ספרות "


def _is_english_chars(string):
    try:
        string.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


class EnglishCharsValidator:
    """
    Validate whether the password is of a minimum length.
    """
    def validate(self, password, user=None):
        if not _is_english_chars(password):
            raise ValidationError("על הסיסמא להכיל אותיות באנגלית וספרות בלבד",
                                  code='non-english-chars',
                                  )

    def get_help_text(self):
        return "על הסיסמא להכיל אותיות באנגלית וספרות בלבד"
