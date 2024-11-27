from django.db import models
from django.utils.text import slugify
from modules.serializers import get_serializer_for_model


class Store(models.Model):
    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    avatar = models.ForeignKey("cdn.Image", on_delete=models.SET_NULL, related_name="store_image", blank=True, null=True)
    social_links = models.ManyToManyField("UserSocialMedia", related_name="store", blank=True)
    describe = models.TextField(blank=True)
    owner = models.ForeignKey("user.User", related_name="store", on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return f"{self.name}"


    def as_dict(self, fields=None):
        fields = fields or ['id','slug','name','avatar','describe']
        data = get_serializer_for_model(queryset=self, model=Store, fields=fields, many=False)
        data.data["avatar"] = self.avatar.get_absolute_url() if self.avatar else None
        return data.data
    def as_mini_dict(self, fields=None):
        fields = fields or ['id','slug','name','avatar']
        data = get_serializer_for_model(queryset=self, model=Store, fields=fields, many=False)
        data.data["avatar"] = self.avatar.get_absolute_url() if self.avatar else None
        return data.data

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    



class Goods(models.Model):
    store = models.ForeignKey("Store", related_name="goods", on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True,)
    price = models.DecimalField(max_digits=10, blank=True, decimal_places=2)
    poster = models.ForeignKey("cdn.Image", on_delete=models.SET_NULL, related_name="goods_image", blank=True, null=True)
    gallery = models.ManyToManyField("Gallery", related_name="goods", blank=True)
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
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

    def as_dict(self, fields=None):
        fields = fields or ['id', 'slug', 'title', 'price', 'poster', 'description', 'views_count', 'bought_count', 'store', 'date_published', 'date_updated']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data.data["store"] = self.store.as_dict()
        data.data["poster"] = self.poster.build_img_url() if self.poster else None
        data.data['characteristic'] = [ch.as_dict() for ch in self.characteristic.all()]
        data.data['category'] = [cat.as_dict() for cat in self.category.all()]
        data.data['gallery'] = [img.as_dict() for img in self.gallery.all()]
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['id', 'slug', 'title', 'price', 'poster', 'views_count', 'store', 'date_published', 'date_updated']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data.data["poster"] = self.poster.build_img_url() if self.poster else None
        data.data["store"] = self.store.as_mini_dict()
        return data.data



class Gallery(models.Model):
    img = models.ForeignKey("cdn.Image", on_delete=models.SET_NULL, related_name="goods_gallery_image", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def as_dict(self, fields=None):
        fields = fields or ['img', 'date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['img']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data


class Characteristic(models.Model):
    name_type = models.ForeignKey("CharacteristicNameType", on_delete=models.CASCADE, related_name="characteristic")
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
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['name', 'slug', 'id']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data


class UserSocialMedia(models.Model):
    social = models.ForeignKey("SocialMedia", related_name="user_social_media", on_delete=models.CASCADE, blank=True)
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
