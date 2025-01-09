from . import models
from store import models as store_models
from django.contrib.auth import authenticate, login as auth_login_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from modules.mail import mail
from modules.validators import validator
from modules.serializers import get_serializer_for_model
from modules.html import render
from django.utils.decorators import method_decorator
from modules.decorators.user_decorators import user_required



class UserLogin(APIView):
    def post(self, request: HttpRequest):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login_user(request, user)
            session_key = request.session.session_key
            return Response({"status": True, "id": user.pk, "user_token": session_key,})
        else:
            return Response({"status": False, "message": "Логін або пароль не співпадають з нашими", "username": username, "password": password})


class UserRegister(APIView):
    def post(self, request: HttpRequest):
        if request.GET.get("step") == "1":
            username = request.data.get('username')
            email = request.data.get('email')
            is_email = models.User.objects.filter(email=email).exists()
            is_username = models.User.objects.filter(username=username).exists()
            
            if is_email or is_username:
                return Response({"status": False, "is_email": is_email, "is_username": is_username})
            validated_email = models.ValidatedEmails(email=email)
            validated_email.save()
            html_content = render.render_html(template="mail/validated_email.html", context={"username":username, "validated_email_code":validated_email.code})
            new_mail = mail.Email(
                subject="Підтвердження реєстрації на сайті CraftStore", 
                html_content=html_content,
                recipient_email=email
            )
            status = new_mail.send_email()
            return Response({"status": status, "id": validated_email.pk})
        elif request.GET.get("step") == "2":
            email = request.data.get('email')
            code = request.data.get('code')
            validated_email = models.ValidatedEmails.objects.filter(email=email, code=code)
            if validated_email.exists():
                validated_email = validated_email.first()
                validated_email.delete()
                return Response({"status": True})
            return Response({"status": False, "code": 404, "message": "Invalid code"})
        elif request.GET.get("step") == "3":
            username = request.data.get("username")
            email = request.data.get("email")
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            gender = request.data.get('gender')
            phone_number = request.data.get('phone_number')
            password = request.data.get("password")
            repeat_password = request.data.get("repeat_password")
            if len(username) <= 2:
                return Response({"status": False, "message": "Логін має бути більше 2 букв"})
            if "." not in email or "@" not in email:
                return Response({"status": False, "message": "Невірна електронна скринька"})
            if password != repeat_password:
                return Response({"status": False, "message": "Паролі не співпадають"})
            validatet_password_status, validatet_password_message = validator.validate_password(password=password)
            if not validatet_password_status:
                return Response({"status": False, "message": validatet_password_message})
            user = models.User.objects.filter(email=email)
            if user.exists():
                return Response({"status": False, "message": f"Email {email} Уже зареєстровано"})
            user = models.User.objects.filter(username=username)
            if user.exists():
                return Response({"status": False, "message": f"Користувач {username} Уже зареєстрований"})
            user = models.User()
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.user_gender = gender
            user.phone_number = phone_number
            user.set_password(password)
            user.save()
            auth_login_user(request, user)
            session_key = request.session.session_key
            return Response({"status": True, "message": "Дякуємо за реєстрацію!", "id": user.pk, "user_token": session_key,})
        return Response({"status": False, "message": "Invalid step", "code": 404,}, status=400)


class UserEdit(APIView):
    @method_decorator(user_required)
    def post(self, request: HttpRequest):
        email_status, phone_status = False
        email = request.data.get("email")
        phone_number = request.data.get('phone_number')
        user = request.user
        if email:
            email_status = validator.validate_email(email=email)
            if email_status:
                user.email = email
        if phone_number:
            phone_status = validator.valite_phone_number(phone=phone_number)
            if phone_status:
                user.phone_number = phone_number
        user.save()
        return Response({"email_status": email_status, "phone_status": phone_status})



class UserResetPassword(APIView):
    def post(self, request: HttpRequest):
        if request.GET.get("step") == "1":
            email = request.data.get("email")
            email_status = validator.validate_email(email=email)
            if not email_status or not models.User.objects.filter(email=email).exists():
                return Response({"status": False, "message": "Bad email"})
            user = models.User.objects.get(email=email)
            password = models.MailCode(user=user)
            password.save()
            html_content = render.render_html("mail/reset_password.html", context={"user": user, "password": password})
            new_mail = mail.Email(
                subject="Скидання паролю на сайті CraftStore", 
                html_content=html_content,
                recipient_email=email
            )
            status = new_mail.send_email()
            return Response({"status": status,})
        if request.GET.get("step") == "2":
            email = request.data.get("email")
            email_status = validator.validate_email(email=email)
            if not email_status or not models.User.objects.filter(email=email).exists():
                return Response({"status": False, "message": "Bad email"})
            user = models.User.objects.get(email=email)
            code = request.data.get("code")
            password = models.MailCode.objects.filter(user=user, code=code)
            if not password.exists():
                return Response({"status": False, "code": 404})
            password = password.first()
            return Response({"status": True, "password_id": password.pk})
        if request.GET.get("step") == "3":
            password_id = request.data.get("password_id")
            new_password = request.data.get("new_password")
            new_repeat_password = request.data.get("repeat_password")
            password = models.MailCode.objects.filter(pk=password_id)
            if not password.exists():
                return Response({"status": False, "code": 404})
            password = password.first()
            validatet_password_status, validatet_password_message = validator.validate_password(password=new_password)
            if not validatet_password_status:
                return Response({"success": False, "message": validatet_password_message})
            if new_password != new_repeat_password:
                return Response({"success": False, "message": "Паролі не співпадають"})
            user = password.user
            user.set_password(new_password)
            user.save()
            password.delete()
            return Response({"status": True})


class User(APIView):
    @method_decorator(user_required)
    def get(self, request: HttpRequest):
        serializer = get_serializer_for_model(queryset=request.user, 
                                              model=models.User,
                                              fields=["avatar", "username", "first_name", "last_name", "is_active", "last_login", "date_joined"], 
                                              many=False)
        return Response(serializer.data)


class UserFavoritesAPI(APIView):
    @method_decorator(user_required)
    def get(self, request: HttpRequest):
        user = request.user
        data = {"count": user.favorites.count(),"goods":[]}
        for goods in user.favorites.all():
            data["goods"].append(goods.goods.as_mini_dict(fields=["poster", "slug", "title", "price", "views_count", "date_published", "store"]))
        return Response(data)
    @method_decorator(user_required)
    def post(self, request: HttpRequest):
        user = request.user
        good_slug = request.data.get("good_slug")
        if not store_models.Goods.objects.filter(slug=good_slug).exists():
            return Response({"status": False, "code": 404})
        goods = store_models.Goods.objects.filter(slug=good_slug)
        usergoods = models.UserGoods.objects.get_or_create(goods=goods, user_favorites=user)
        user.favorites.add(usergoods)
        user.save()
        return Response({"status": True})
    @method_decorator(user_required)
    def delete(self, request: HttpRequest):
        user = request.user
        good_slug = request.data.get("good_slug")
        if not store_models.Goods.objects.filter(slug=good_slug).exists():
            return Response({"status": False, "code": 404})
        goods = store_models.Goods.objects.filter(slug=good_slug)
        usergoods = models.UserGoods.objects.filter(goods=goods, user_favorites=user)
        if not usergoods.exists():
            return Response({"status": False, "code": 400})
        usergoods.first().delete
        return Response({"status": True})


class UserHistoryAPI(APIView):
    @method_decorator(user_required)
    def get(self, request: HttpRequest):
        user = request.user
        data = {"count": user.user_views_history.count(),"goods":[]}
        for goods in user.user_views_history.all():
            data["goods"].append(goods.goods.as_mini_dict(fields=["poster", "slug", "title", "price", "views_count", "date_published", "store"]))
        return Response(data)


class UserCartAPI(APIView):
    @method_decorator(user_required)
    def get(self, request: HttpRequest):
        user = request.user
        data = {"count": user.cart.count(),"goods":[]}
        for goods in user.cart.all():
            data["goods"].append(goods.goods.as_mini_dict(fields=["poster", "slug", "title", "price", "views_count", "date_published", "store"]))
        return Response(data)
    @method_decorator(user_required)
    def post(self, request: HttpRequest):
        user = request.user
        good_slug = request.data.get("good_slug")
        if not store_models.Goods.objects.filter(slug=good_slug).exists():
            return Response({"status": False, "code": 404})
        goods = store_models.Goods.objects.filter(slug=good_slug)
        usergoods, created = models.UserGoods.objects.get_or_create(goods=goods, user_cart=user)
        if created:
            user.cart.add(usergoods)
            user.save()
        else:
            usergoods.count =+ 1
        return Response({"status": True, "count":usergoods.count, "good_slug": good_slug})
    @method_decorator(user_required)
    def delete(self, request: HttpRequest):
        user = request.user
        good_slug = request.data.get("good_slug")
        if not store_models.Goods.objects.filter(slug=good_slug).exists():
            return Response({"status": False, "code": 404})
        goods = store_models.Goods.objects.filter(slug=good_slug)
        usergoods = models.UserGoods.objects.filter(goods=goods, user_cart=user)
        if not usergoods.exists():
            return Response({"status": False, "code": 400})
        usergoods = usergoods.first()
        if usergoods.count > 1:
            usergoods.count =- 1
            usergoods.save()
            return Response({"status": True, "count":usergoods.count, "good_slug": good_slug})
        else:
            usergoods.delete()
        return Response({"status": True})
