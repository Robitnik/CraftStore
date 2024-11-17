import re

def validate_email(email):
    try:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(email_regex, email):
            return True
        else:
            return False
    except Exception:
        return False
    

def valite_phone_number(phone):
    str_phone = str(phone)
    if len(str_phone) > 14 and len(str_phone) < 16:
        return True
    return False


def validate_password(password):
    if len(password) < 8:
        return False, "Пароль повинен містити щонайменше 8 символів."

    if not re.search(r'[A-Z]', password):
        return False, "Пароль повинен містити хоча б одну велику літеру."

    if not re.search(r'[a-z]', password):
        return False, "Пароль повинен містити хоча б одну малу літеру."

    if not re.search(r'[0-9]', password):
        return False, "Пароль повинен містити хоча б одну цифру."

    if not re.search(r'[\W_]', password):
        return False, "Пароль повинен містити хоча б один спеціальний символ."

    return True, "Пароль валідний."