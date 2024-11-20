from django.db import models
from django.utils.text import slugify


class Store(models.Model):
    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    avatar = models.ForeignKey("cdn.Image", on_delete=models.SET_NULL, related_name="image", blank=True, null=True)
    social_links = models.ManyToManyField("UserSocialMedia", related_name="store", blank=True)
    describe = models.TextField(blank=True)
    owner = models.ForeignKey("user.User", related_name="store", on_delete=models.CASCADE, blank=True)

    def __str__(self) -> str:
        return f"{self.name}"


    def as_dict(self):
        data = {
            'id': self.pk,
            'slug': self.slug,
            'name': self.name,
            'avatar': self.avatar,
            'describe': self.describe,
        }
        return data
    def as_mini_dict(self):
        data = {
            'id': self.pk,
            'slug': self.slug,
            'name': self.name,
        }
        return data

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    



class Goods(models.Model):
    store = models.ForeignKey("Store", related_name="goods", on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True,)
    price = models.DecimalField(max_digits=10, blank=True, decimal_places=2)
    poster = models.ForeignKey("cdn.Image", on_delete=models.SET_NULL, related_name="image", blank=True, null=True)
    gallery = models.ManyToManyField("Gallery", related_name="goods", blank=True)
    description = models.TextField(blank=True)
    views_count = models.IntegerField(default=0)
    bought_count = models.IntegerField(default=0)
    characteristic = models.ManyToManyField("Characteristic", related_name="goods", on_delete=models.CASCADE, blank=True)
    category = models.ManyToManyField("Category", related_name="goods", blank=True,)
    published = models.BooleanField(default=True)
    count = models.IntegerField(default=0, blank=True, null=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

    def as_dict(self):
        data = {
            'id': self.pk,
            'slug': self.slug,
            'title': self.title,
            'price': self.price,
            'poster': self.poster,
            'description': self.description,
            'views_count': self.views_count,
            'bought_count': self.bought_count,
            'store':  self.store.as_mini_dict(),
            #'characteristic': [ch.as_dict() for ch in self.characteristic.all()],
            #'category': [ch.as_dict() for ch in self.category.all()],
            #'gallery': [ch.as_dict() for ch in self.gallery.all()],
            'date_published': self.date_published,
            'date_updated': self.date_updated,
        }
        return data
    def as_mini_dict(self):
        data = {
            'id': self.pk,
            'slug': self.slug,
            'title': self.title,
            'price': self.price,
            'poster': self.poster,
            'views_count': self.views_count,
            'store':  self.store.as_mini_dict(),
            'date_published': self.date_published,
            'date_updated': self.date_updated,
        }
        return data



class Gallery(models.Model):
    path = models.ForeignKey("cdn.Image", on_delete=models.SET_NULL, related_name="image", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)



class Characteristic(models.Model):
    name_type = models.ForeignKey("CharacteristicNameType", on_delete=models.CASCADE, related_name="characteristic")
    value = models.CharField(max_length=1000, blank=True)


class CharacteristicNameType(models.Model):
    name = models.CharField(max_length=500, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=500, blank=True)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class UserSocialMedia(models.Model):
    social = models.ForeignKey("SocialMedia", related_name="user_social_media", on_delete=models.CASCADE, blank=True)
    link = models.CharField(max_length=200, blank=True)



class SocialMedia(models.Model):
    name = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=150, blank=True)