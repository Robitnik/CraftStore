from user.models import User
from store.models import Store, Goods, Category
from cdn.models import Image
from django.utils.text import slugify
from django.http import HttpRequest
from modules.files import save_uploaded_file
from cdn.utils import image_to_cloud
from modules.mail import mail
from modules.html import render
from user.models import MailCode



class UserStore:
    def __init__(self, user: User) -> None:
        self.user = user
    def create_store(self, request: HttpRequest) -> dict:
        if Store.objects.filter(owner=self.user).exists():
            return {"status": False, "message": "Ви не можете створити білше 1 магазину", "code": 301}
        if request.GET.get("step") == "1":
            data = request.data
            if not data.get("slug"):
                return {"status": False, "message": "Не отримано ID", "code": 405}
            slug = slugify(data.get("slug"))
            store = Store.objects.filter(slug__exact=slug)
            if store.exists():
                return {"status": False, "message": "Магазин з такою назвою вже зареєстровано", "code": 301}
            return {"status": True, "slug": slug}
        if request.GET.get("step") == "2":
            data = request.data
            store_name = data.get("store_name")
            store_slug = data.get("store_slug")
            store_logo_id = data.get("store_logo_id")
            store = Store()
            store.avatar = Image.objects.get(pk=store_logo_id) if store_logo_id and Image.objects.filter(pk=store_logo_id).exists() else None
            store.name = store_name
            store.slug = store_slug
            store.owner = self.user
            store.save()
            return {"status": True, "store": store.as_dict(fields=['slug','name','avatar'])}


    def delete_store(self, request: HttpRequest) -> dict:
        if request.GET.get("step") == "1":
            mailcode = MailCode(user=self.user).save()
            html_content = render.render_html("mail/verify_delete_store.html", context={"username": self.user.username, "validated_code": mailcode.code})
            new_mail = mail.Email(
                subject="Закриття магазину на сайті CraftStore", 
                html_content=html_content,
                recipient_email=self.user.email
            )
            status = new_mail.send_email()
            return {"status": status}
        if request.GET.get("step") == "2":
            data = request.data
            code = data.get("code")
            if MailCode.objects.filter(user=self.user, code=code).exists():
                store = Store.objects.get(owner=self.user)
                for good in store.goods.all():
                    good.delete()
                store.delete()
                return {"status": True}


class StoreGood:
    def __init__(self, store: Store, user: User):
        self.store = store
        self.user = user
    def add_good(self, request: HttpRequest) -> dict:
        if self.store.owner != self.user:
            return {"status": False, "code": 400}
        data = request.data
        good: Goods = Goods()
        poster = Image.objects.get(pk=data.get("poster")) if data.get("poster") and Image.objects.filter(pk=data.get("poster")).exists() else None
        gallery = (
            [Image.objects.get(pk=pk) for pk in data.get("gallery")]
            if data.get("gallery") and Image.objects.filter(pk__in=data.get("gallery")).exists()
            else []
        )
        categories = [Category.objects.get(pk=pk) for pk in data.get("category")] if data.get("category") and Category.objects.filter(pk__in=data.get("category")).exists() else []
        good.title = data.get("title")
        good.price = data.get("price")
        good.count = data.get("count")
        good.description = data.get("description")
        good.author = self.user
        good.store = self.store
        good.poster = poster
        good.save()
        good.gallery.set(gallery)
        good.category.set(categories)
        good.store = self.store
        good.save()
        return {"status": True, "good": good.as_dict()}
    def delete_good(self, request: HttpRequest) -> dict:
        if self.store.owner != self.user:
            return {"status": False, "code": 400}
        data = request.data
        pk = data.get("id")
        if not pk:
            return {"status": False,"code": 404, "massage":"good not found"}
        if not Goods.objects.filter(pk=pk).exists():
            return {"status": False,"code": 404, "massage":"good not found"}
        good = Goods.objects.get(pk=pk, store=self.store)
        good.delete()
        return {"status": True}
    def hide_good(self, request: HttpRequest) -> dict:
        data = request.data
        pk = data.get("id")
        if not pk:
            return {"status": False,"code": 404, "massage":"good not found"}
        if not Goods.objects.filter(pk=pk).exists():
            return {"status": False,"code": 404, "massage":"good not found"}
        good = Goods.objects.get(pk=pk, store=self.store)
        if good.author != self.user and self.store.owner != self.user:
            return {"status": False, "code": 400}
        good.published = False
        good.save()
        return {"status": True, "good": good.as_dict()}
    def unhide_good(self, request: HttpRequest) -> dict:
        data = request.data
        pk = data.get("id")
        if not pk:
            return {"status": False,"code": 404, "massage":"good not found"}
        if not Goods.objects.filter(pk=pk).exists():
            return {"status": False,"code": 404, "massage":"good not found"}
        good = Goods.objects.get(pk=pk, store=self.store)
        if good.author != self.user and self.store.owner != self.user:
            return {"status": False, "code": 400}
        good.published = True
        good.save()
        return {"status": True, "good": good.as_dict()}
    def update_good(self, request: HttpRequest) -> dict:
        data = request.data
        pk = data.get("id")
        return {"status": False}


