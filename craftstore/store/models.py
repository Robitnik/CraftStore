from django.db import models
from modules.serializers import get_serializer_for_model
from modules.db.text import slugify

class Store(models.Model):
    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    avatar = models.OneToOneField("cdn.Image", on_delete=models.SET_NULL, related_name="store_image", blank=True, null=True)
    social_links = models.ManyToManyField("UserSocialMedia", related_name="store", blank=True)
    describe = models.TextField(blank=True)
    owner = models.OneToOneField("user.User", related_name="store", on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return f"{self.name}"


    def as_dict(self, fields=None):
        fields = fields or ['id','slug','name','describe']
        data = get_serializer_for_model(queryset=self, model=Store, fields=fields, many=False)
        data = dict(data.data)
        data["avatar"] = self.avatar.build_img_url() if self.avatar else None
        return data
    def as_mini_dict(self, fields=None):
        fields = fields or ['id','slug','name']
        data = get_serializer_for_model(queryset=self, model=Store, fields=fields, many=False)
        data = dict(data.data)
        data["avatar"] = self.avatar.build_img_url() if self.avatar else None
        return data

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    



class Goods(models.Model):
    store = models.ForeignKey("Store", related_name="goods", on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True,)
    price = models.DecimalField(max_digits=10, blank=True, decimal_places=2)
    poster = models.OneToOneField("cdn.Image", on_delete=models.SET_NULL, related_name="goods_image", blank=True, null=True)
    gallery = models.ManyToManyField("cdn.Image", related_name="goods_images", blank=True)
    description = models.TextField(blank=True)
    views_count = models.IntegerField(default=0)
    bought_count = models.IntegerField(default=0)
    characteristic = models.ManyToManyField("Characteristic", related_name="goods", blank=True)
    category = models.ManyToManyField("Category", related_name="goods", blank=True,)
    published = models.BooleanField(default=True)
    count = models.IntegerField(default=0, blank=True, null=True)
    author = models.ForeignKey("user.User", related_name="goods", on_delete=models.SET_NULL, null=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.pk}")
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
    

    def as_dict(self, fields=None):
        fields = fields or ['id', 'slug', 'title', 'price', 'poster', 'description', 'views_count', 'bought_count', 'store', 'date_published', 'date_updated']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = dict(data.data)
        data["store"] = self.store.as_dict()
        data["poster"] = self.poster.build_img_url() if self.poster else None
        data['characteristic'] = [ch.as_dict() for ch in self.characteristic.all()]
        data['category'] = [cat.as_dict() for cat in self.category.all()]
        data['gallery'] = [img.build_img_url() for img in self.gallery.all()]
        return data

    def as_mini_dict(self, fields=None):
        fields = fields or ['id', 'slug', 'title', 'price', 'poster', 'views_count', 'store', 'date_published', 'date_updated']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = dict(data.data)
        data["poster"] = self.poster.build_img_url() if self.poster else None
        data["store"] = self.store.as_mini_dict()
        return data


    def user_info(self, user):
        """
        Повертає інформацію про товар для заданого користувача.
        """
        info = {
            "is_favorite": False,
            "is_viewed": False,
            "cart": {"is_in_cart": False, "quantity": 0}
        }
        # Якщо користувача немає або він не аутентифікований – повертаємо стандартне значення.
        if not user or not user.is_authenticated:
            return info

        # Перевірка, чи товар є в улюблених.
        # Припускаємо, що у користувача є related_name 'favorites' для моделі FavoriteItem.
        if user.favorites.filter(goods=self).exists():
            info["is_favorite"] = True

        # Перевірка, чи товар є в історії переглядів.
        # Припускаємо, що у користувача є related_name 'goods_history' для моделі HistoryItem.
        if user.goods_history.filter(goods=self).exists():
            info["is_viewed"] = True

        # Перевірка, чи товар знаходиться в кошику.
        # Припускаємо, що у користувача є related_name 'cart' для моделі UserCart,
        # а модель UserCart містить поле 'quantity'.
        cart_item = user.cart.filter(goods=self).first()
        if cart_item:
            info["cart"]["is_in_cart"] = True
            info["cart"]["quantity"] = cart_item.quantity

        return info


class Characteristic(models.Model):
    name_type = models.OneToOneField("CharacteristicNameType", on_delete=models.SET_NULL, null=True, blank=True, related_name="characteristic")
    value = models.CharField(max_length=1000, blank=True)

    def as_dict(self, fields=None):
        fields = fields or ['name_type', 'value']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['name_type']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data


class CharacteristicNameType(models.Model):
    name = models.CharField(max_length=500, blank=True)

    def as_dict(self, fields=None):
        fields = fields or ['name']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['name']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data


class Category(models.Model):
    name = models.CharField(max_length=500, blank=True)
    slug = models.SlugField(max_length=100, blank=True)
    parent_category = models.ForeignKey("Category", related_name="sub_categories", on_delete=models.SET_NULL, blank=True, null=True)
    description = models.TextField(blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def as_dict(self, fields=None):
        fields = fields or ['name', 'slug', 'id', 'description', 'date_published', 'date_updated']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = dict(data.data)
        data["is_super"] = True if not self.parent_category else False
        if self.parent_category:
            data["parent_category"] = self.parent_category.as_mini_dict()
        return data

    def as_mini_dict(self, fields=None):
        fields = fields or ['name', 'slug', 'id']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = dict(data.data)
        return data

    def __str__(self):
        return f"{self.name} - {self.slug}"

class UserSocialMedia(models.Model):
    social = models.OneToOneField("SocialMedia", related_name="user_social_media", on_delete=models.SET_NULL, blank=True, null=True)
    link = models.CharField(max_length=200, blank=True)

    def as_dict(self, fields=None):
        fields = fields or ['social', 'link']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['social']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data


class SocialMedia(models.Model):
    name = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=150, blank=True)

    def as_dict(self, fields=None):
        fields = fields or ['name', 'icon']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['name']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data
