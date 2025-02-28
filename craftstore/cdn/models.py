from django.db import models
from django.urls import reverse
from modules.config import cdn_domain
from modules.generators.strings import generate_random_string
from modules.images.convertor import image_to_webp
from modules.serializers import get_serializer_for_model


class Cloud(models.Model):
    name = models.CharField(max_length=300, blank=True)
    bucket_name = models.CharField(max_length=300, blank=True)
    application_key_id = models.CharField(max_length=300, blank=True)
    application_key = models.CharField(max_length=300, blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True,)
    host_server = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.status} - {self.created_at}"


    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Хмари"
        verbose_name_plural = "Хмару"


class Image(models.Model):
    cloud = models.ForeignKey("Cloud", on_delete=models.SET_NULL, related_name="image", blank=True, null=True, default=1)
    path = models.ImageField(blank=True, upload_to="static", null=True)
    url = models.CharField(max_length=1000, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True)
    author = models.ForeignKey("user.USER", related_name="images", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Картинку"
        verbose_name_plural = "Картинки"

    def __str__(self):
        return f"{self.pk} - {self.url}"

    def build_img_url(self):
        return f"{cdn_domain}/{self.url}"

    def get_absolute_url(self):
        return self.build_img_url()

    def as_dict(self, fields=None):
        fields = fields or ['id', 'create_at', 'slug']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = data.data
        data['url'] = self.build_img_url()
        data['author'] = self.author.as_mini_dict() if self.author else None
        return data

    def as_mini_dict(self, fields=None):
        fields = fields or ['id', 'slug']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = data.data
        data['url'] = self.build_img_url()
        return data


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from modules.cloud.b2 import upload_file
        import os
        if not self.slug:
            slug = generate_random_string(len1=8, len2=16)
            while Image.objects.filter(slug=slug).exists():
                slug = generate_random_string(len1=8, len2=16)
            self.slug = slug
        if not self.cloud:
            self.cloud = Cloud.objects.first()
        if self.url:
            if ".webp" in self.url:
                self.url = str(self.url.replace(".webp", ""))
                self.url = f"{self.url}_{self.slug}_{self.pk}.webp"
            else:
                self.url = f"{self.url}_{self.slug}_{self.pk}.webp" if self.url else f"{self.slug}_{self.pk}.webp"
        if not self.url:
            self.url = f"images/{self.slug}_{self.pk}.webp"

        path = image_to_webp(image_path=self.path.path)
        upload_file(file_path=path, end_file_path=self.url, cloud_id=self.cloud.pk)
        try:
            if path:
                os.remove(path)
                self.path = None
        except Exception:
            pass
        return super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        from modules.cloud.b2 import delete_file
        status, message = delete_file(file_path=self.url, cloud_id=self.cloud.pk)
        if not status:
            return status, message
        super().delete(*args, **kwargs)
        return True, True