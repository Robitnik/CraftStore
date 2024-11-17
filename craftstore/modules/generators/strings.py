import random
import string


def generate_random_string(len1=30, len2=50):
    length = random.randint(len1, len2)
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def generate_number_string(num_digits=6):
    first_digit = random.randint(1, 9)
    other_digits = [random.randint(0, 9) for _ in range(num_digits - 1)]
    result = str(first_digit) + ''.join(map(str, other_digits))
    return str(result)
