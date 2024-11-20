import os
from modules.config import files_dir
def save_uploaded_file(uploaded_file, file_name=None):
    if not uploaded_file:
        return False, "Не отримано файл"
    file_path = os.path.join(files_dir, file_name or uploaded_file.name)
    with open(file_path, 'wb') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return file_path