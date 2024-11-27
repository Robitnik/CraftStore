from PIL import Image


def image_to_webp(image_path, compression_quality=80, width=None, height=None):
    try:
        img = Image.open(image_path)
        if width or height:
            img = img.resize((width if width else img.width, height if height else img.height))
        output_path = image_path.rsplit('.', 1)[0] + '.webp'
        img.save(output_path, 'WebP', quality=compression_quality)
        return output_path
    except Exception as e:
        return False

