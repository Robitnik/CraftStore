from user.models import User
from store.models import Store
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
        if request.GET.get("step") == "1":
            if Store.objects.filter(owner=self.user).exists():
                return {"status": False, "message": "Ви не можете створити білше 1 магазину", "code": 301}
            data = request.data
            slug = slugify(data.get("store_name"))
            store = Store.objects.filter(slug__exact=slug)
            if store.exists():
                return {"status": False, "message": "Магазин з такою назвою вже зареєстровано", "code": 301}
            return {"status": True, "slug": slug}
        if request.GET.get("step") == "2":
            data = request.data
            store_name = data.get("store_name")
            store_slug = data.get("store_slug")
            store_logo_path = save_uploaded_file(request.FILES.GET("store_logo")) if request.FILES.GET("store_logo") else None
            store = Store()
            store.avatar = image_to_cloud(store_logo_path, url=f"images/store/{store_slug}/logo/") if store_logo_path else None
            store.name = store_name
            store.slug = store_slug
            store.owner = self.user
            store.save()
            return {"status": True, "store": store.as_dict()}


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