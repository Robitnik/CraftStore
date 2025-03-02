from django.db import models
from django.contrib.auth.models import AbstractUser, Group as AbstractGroup
from modules.enycryptor import FernetEncryptor
from modules.generators.strings import generate_number_string, generate_random_string
from django.utils.text import slugify
from django.contrib.auth.hashers import is_password_usable
from modules.serializers import get_serializer_for_model


class User(AbstractUser):
    avatar = models.OneToOneField("cdn.Image", on_delete=models.SET_NULL, related_name="image", blank=True, null=True)
    groups = models.ManyToManyField('user.Group', related_name='users', blank=True)
    address = models.CharField(max_length=1000, blank=True)
    phone_number = models.CharField(max_length=1000, blank=True)
    user_gender = models.CharField(max_length=1000, blank=True)
    slug = models.SlugField(blank=True)
    def is_online(self):
        return True

    def get_decrypt_cypher(self, cypher):
        if cypher:
            return FernetEncryptor().decrypt(cypher)
        return None

    def __str__(self) -> str:
        return super().__str__()

    def save(self, *args, **kwargs):
        if self.password and not is_password_usable(self.password):
            self.set_password(self.password)
        if not self.slug:
            self.slug = slugify(self.username, allow_unicode=False)
        super().save(*args, **kwargs)

    def get_avatar_url(self):
        return self.avatar.build_img_url() if self.avatar else None

    def as_dict(self, fields=None):
        fields = fields or ['username', 'id', 'slug', 'avatar', 'address', 'phone_number', 'user_gender']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data.data['avatar'] = self.get_avatar_url()
        data.data['groups'] = [group.as_mini_dict() for group in self.groups.all()]
        data.data['favorites'] = [fav.as_dict() for fav in self.favorite_items.all()]
        data.data['views_history'] = [view.as_dict() for view in self.history_items.all()]
        data.data['cart'] = [item.as_dict() for item in self.cart_items.all()]
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['username', 'id', 'slug', 'avatar']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data.data['avatar'] = self.get_avatar_url()
        return data.data


class UserCart(models.Model):
    user = models.ForeignKey("User", related_name="cart", on_delete=models.CASCADE)
    goods = models.ForeignKey("store.Goods", on_delete=models.SET_NULL, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def as_dict(self, fields=None):
        return {"date": self.date_added, "goods": self.goods.as_dict(fields)}

    def as_mini_dict(self, fields=None):
        return {"date": self.date_added, "goods": self.goods.as_mini_dict(fields)}


class UserFavorite(models.Model):
    user = models.ForeignKey("User", related_name="favorites", on_delete=models.CASCADE)
    goods = models.ForeignKey("store.Goods", on_delete=models.SET_NULL, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def as_dict(self, fields=None):
        return {"date": self.date_added, "goods": self.goods.as_dict(fields)}

    def as_mini_dict(self, fields=None):
        return {"date": self.date_added, "goods": self.goods.as_mini_dict(fields)}


class UserGoodHistory(models.Model):
    user = models.ForeignKey("User", related_name="goods_history", on_delete=models.CASCADE)
    goods = models.ForeignKey("store.Goods", on_delete=models.SET_NULL, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def as_dict(self, fields=None):
        return {"date": self.date_added, "goods": self.goods.as_dict(fields)}

    def as_mini_dict(self, fields=None):
        return {"date": self.date_added, "goods": self.goods.as_mini_dict(fields)}



class Group(AbstractGroup):
    def __str__(self) -> str:
        return super().__str__()

    def as_dict(self, fields=None):
        fields = fields or ['id', 'name']
        return get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)

    def as_mini_dict(self, fields=None):
        fields = fields or ['id', 'name']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data



class ValidatedEmails(models.Model):
    email = models.EmailField(blank=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    code = models.CharField(blank=True, max_length=20)

    def save(self, *args, **kwargs) -> None:
        if not self.code:
            self.code = generate_number_string(num_digits=6)
        super().save(*args, **kwargs)

    def as_dict(self, fields=None):
        fields = fields or ['email', 'status', 'date', 'code']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['email', 'status']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data


class MailCode(models.Model):
    code = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date_pub = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_number_string(num_digits=6)
        super().save(*args, **kwargs)

    def as_dict(self, fields=None):
        fields = fields or ['code', 'user', 'date_pub', 'date_updated']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data.data['user'] = self.user.as_mini_dict()
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['code', 'date_pub']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data