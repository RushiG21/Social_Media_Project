from django.core.exceptions import ValidationError
import re

class MinimumNumberValidator:
    def __init__(self, min_digits=1):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if len(re.findall(r'\d', password)) < self.min_digits:
            raise ValidationError(
                f'Password must contain at least {self.min_digits} digit(s).',
                code='password_no_number',
            )

    def get_help_text(self):
        return f'Your password must contain at least {self.min_digits} digit(s).'


class MinimumUppercaseValidator:
    def __init__(self, min_uppercase=1):
        self.min_uppercase = min_uppercase

    def validate(self, password, user=None):
        if len(re.findall(r'[A-Z]', password)) < self.min_uppercase:
            raise ValidationError(
                f'Password must contain at least {self.min_uppercase} uppercase letter(s).',
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return f'Your password must contain at least {self.min_uppercase} uppercase letter(s).'


class MinimumLowercaseValidator:
    def __init__(self, min_lowercase=1):
        self.min_lowercase = min_lowercase

    def validate(self, password, user=None):
        if len(re.findall(r'[a-z]', password)) < self.min_lowercase:
            raise ValidationError(
                f'Password must contain at least {self.min_lowercase} lowercase letter(s).',
                code='password_no_lowercase',
            )

    def get_help_text(self):
        return f'Your password must contain at least {self.min_lowercase} lowercase letter(s).'


class SymbolValidator:
    def __init__(self, min_symbols=1):
        self.min_symbols = min_symbols

    def validate(self, password, user=None):
        if len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', password)) < self.min_symbols:
            raise ValidationError(
                f'Password must contain at least {self.min_symbols} symbol(s).',
                code='password_no_symbol',
            )

    def get_help_text(self):
        return f'Your password must contain at least {self.min_symbols} symbol(s).'
