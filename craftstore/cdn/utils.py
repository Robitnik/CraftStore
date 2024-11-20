from .models import Image


def image_to_cloud(path, url) -> Image:
    img = Image(
        path=path,
        url=url
    )
    img.save()
    return img