import re
from unidecode import unidecode
from transliterate import translit
from django.utils.text import slugify as django_slugify
SPECIAL_CHAR_MAP = {
    "&": "and",
    "@": "at",
    "+": "plus",
    "#": "hash",
    "%": "percent",
    "$": "dollar",
    "€": "euro",
    "£": "pound",
    "₴": "hryvnia",
}

def slugify(text: str) -> str:
    # Якщо є кирилиця, транслітеруємо її
    if re.search(r'[а-яА-ЯёЁіІїЇєЄґҐ]', text):
        text = translit(text, 'ru', reversed=True)

    # Універсальна транслітерація (на випадок латиниці з діакритиками)
    text = unidecode(text)

    # Перетворення в нижній регістр
    text = text.lower()

    # Заміна спецсимволів на текстові еквіваленти
    for char, replacement in SPECIAL_CHAR_MAP.items():
        text = text.replace(char, f"-{replacement}-")

    # Видалення всього, крім літер, цифр і дефісів
    text = re.sub(r'[^a-z0-9\-]+', '-', text)

    # Видалення повторюваних дефісів
    text = re.sub(r'-+', '-', text).strip('-')
    text = django_slugify(text)
    return text
