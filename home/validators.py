from django.core.exceptions import ValidationError
import re
class PasswordValidation:
    def __init__(self):
        self.regex_uppercase = r'[A-Z]'  #
        self.regex_special = r'[@$!%*?&]'  
        self.min_length = 8

    def validate(self, password):
        # Check password length
        if len(password) < self.min_length:
            raise ValidationError(f"Password must be at least {self.min_length} characters long.")

        # Check for at least one uppercase letter
        if not re.search(self.regex_uppercase, password):
            raise ValidationError("Password must contain at least one uppercase letter.")

        # Check for at least one special character
        if not re.search(self.regex_special, password):
            raise ValidationError("Password must contain at least one special character.")

        return password