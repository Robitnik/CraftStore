from .models import Image


def image_to_cloud(path, url, author) -> Image:
    img = Image(
        path=path,
        url=url,
        author=author
    )
    img.save()
    return img