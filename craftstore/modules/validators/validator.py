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
    # 1. Перевірка довжини
    if len(password) < 8:
        return False, "Пароль повинен містити щонайменше 8 символів."

    # 2. Перевірка наявності великої літери
    if not re.search(r'[A-Z]', password):
        return False, "Пароль повинен містити хоча б одну велику літеру."

    # 3. Перевірка наявності малої літери
    if not re.search(r'[a-z]', password):
        return False, "Пароль повинен містити хоча б одну малу літеру."

    # 4. Перевірка наявності цифри
    if not re.search(r'[0-9]', password):
        return False, "Пароль повинен містити хоча б одну цифру."

    # 5. Перевірка наявності спецсимволу
    #    (під спецсимволом маємо на увазі символ, що не є літерою/цифрою;
    #     додаємо також підкреслення)
    if not re.search(r'[\W_]', password):
        return False, "Пароль повинен містити хоча б один спеціальний символ."

    # 6. Перевірка списку поширених/легких паролів
    #    (можна розширити цей список на свій розсуд)
    common_passwords = [
        "12345678", "123456789", "11111111", "password", "qwerty",
        "qwertyuiop", "zxcvbnm", "1122333", "abc123", "1q2w3e4r"
    ]
    # Порівнюємо у нижньому регістрі, щоб відловити очевидні варіації
    if password.lower() in common_passwords:
        return False, "Пароль занадто простий або поширений."

    # 7. Перевірка на **поспіль ідучі** символи (прямі або зворотні)
    #    Наприклад, "abcd", "1234" або "dcba", "4321".
    #    Вважаємо, що 4 поспіль ідучі символи - це вже небезпечно простий патерн.
    #    Перевіримо кожен підрядок довжиною 4.
    for i in range(len(password) - 3):
        # Беремо 4 символи
        four_chars = password[i:i+4]
        
        # Згенеруємо стрічку, яка на 1 "крок" від кожного символу
        # і перевіримо, чи вони йдуть послідовно
        asc_seq = "".join(chr(ord(four_chars[0]) + j) for j in range(4))
        desc_seq = "".join(chr(ord(four_chars[0]) - j) for j in range(4))

        if four_chars == asc_seq or four_chars == desc_seq:
            return False, "Пароль містить просту послідовність символів (наприклад, 'abcd' чи '1234')."

    # Якщо всі перевірки пройшли успішно
    return True, "Пароль валідний."
