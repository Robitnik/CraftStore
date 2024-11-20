import os
from modules.config import BASE_DIR


def render_html(template, context):
    template_path = os.path.join(os.path.join(BASE_DIR, "templates"), template)
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            template = file.read()
        return template.format(**context)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{template}' не знайдено.")
    except KeyError as e:
        raise KeyError(f"Не знайдено змінну у контексті: {e}")

