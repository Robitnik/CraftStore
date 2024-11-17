from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser, Group as AbstracGroup
from modules.enycryptor import FernetEncryptor
from modules.generators.strings import generate_number_string, generate_random_string


class User(AbstractUser):
    avatar = models.ForeignKey("cdn.Image", on_delete=models.SET_NULL, related_name="image", blank=True, null=True)
    groups = models.ManyToManyField('user.Group', related_name='users', blank=True)
    address = models.CharField(max_length=1000, blank=True)
    phone_number = models.CharField(max_length=1000, blank=True)
    user_gender = models.CharField(max_length=1000, blank=True)
    favorites = models.ManyToManyField("UserGoods", related_name="user_favorites", blank=True)
    views_history = models.ManyToManyField("UserGoods", related_name="user_views_history", blank=True)
    cart = models.ManyToManyField("UserGoods", related_name="user_cart", blank=True)


    def is_online(self):
        return True

    def get_decrypt_cypher(self, cypher):
        if cypher:
            return FernetEncryptor().decrypt(cypher)
        return None

    def __str__(self) -> str:
        return super().__str__()

    def save(self, *args, **kwargs) -> None:
        return super().save(*args, **kwargs)


class Group(AbstracGroup):
    def __str__(self) -> str:
        return super().__str__()


class UserGoods(models.Model):
    # goods = models.ManyToManyField
    date = models.DateTimeField(auto_now_add=True, blank=True)


class ValidatedEmails(models.Model):
    email = models.EmailField(blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    code = models.CharField(blank=True, max_length=20)
    def save(self, *args, **kwargs) -> None:
        if not self.code:
            self.code = generate_number_string(num_digits=6)
        return super().save(*args, **kwargs)


class Passwords(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,)
    date_pub = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.id = generate_random_string()
        super().save(*args, **kwargs)
