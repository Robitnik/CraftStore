from . import models
from store import models as store_models
from django.contrib.auth import authenticate, login as auth_login_user, logout as auth_logout_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from modules.mail import mail
from modules.validators import validator
from modules.serializers import get_serializer_for_model
from modules.html import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from cdn.models import Image
from rest_framework.authtoken.models import Token
from django.middleware.csrf import get_token
from decimal import Decimal
from django.db.models import Sum


class UserLogin(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            # Створюємо сесію для користувача
            auth_login_user(request, user)
            # Створюємо токен для користувача
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "status": True,
                "id": user.pk,
                "token": token.key,
                "csrfToken": get_token(request),
            })
        else:
            return Response({
                "status": False,
                "message": "Логін або пароль не співпадають",
                "username": username,
            }, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAuthenticated]
    def post(self, request: HttpRequest):
        email_status = False
        phone_status = False
        email = request.data.get("email")
        phone_number = request.data.get('phone_number')
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        avatar_id = request.data.get('avatar_id')
        user = request.user
        if username and user.username!= username:
            if models.User.objects.filter(username=username).exists():
                return Response({"status": False, "message": "Користувач з таким логіном вже існує"})
        if email:
            email_status = validator.validate_email(email=email)
            if email_status:
                if models.User.objects.filter(email=email).exists():
                    return Response({"status": False, "message": "Користувач з таким email вже існує"})
                user.email = email
        if phone_number:
            phone_status = validator.valite_phone_number(phone=phone_number)
            if phone_status:
                if models.User.objects.filter(phone_number=phone_number).exists():
                    return Response({"status": False, "message": "Користувач з таким номером телефону вже існує"})
                user.phone_number = phone_number
        if username:
            user.username = username
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if avatar_id:
            img = Image.objects.filter(pk=avatar_id)
            if img.exists():
                user.avatar = Image.objects.get(pk=avatar_id)
        user.save()
        return Response({"status": True, "user": user.as_dict()})



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
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        data = request.user.as_mini_dict(fields=["username", "first_name", "last_name", "is_active", "last_login", "date_joined"])
        return Response(data)


class UserFavoritesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest):
        user = request.user
        favorites = user.favorites.all()
        data = {
            "count": favorites.count(),
            "goods": [
                fav.goods.as_mini_dict(
                    fields=["poster", "slug", "title", "price", "views_count", "date_published", "store"]
                )
                for fav in favorites
            ]
        }
        return Response(data)

    def post(self, request: HttpRequest):
        user = request.user
        good_id = request.data.get("good_id")
        try:
            goods = store_models.Goods.objects.get(id=good_id)
        except store_models.Goods.DoesNotExist:
            return Response({"status": False, "code": 404})
        
        # Створюємо запис улюбленого товару або повертаємо існуючий
        favorite, created = models.UserFavorite.objects.get_or_create(user=user, goods=goods)
        return Response({"status": True})

    def delete(self, request: HttpRequest):
        user = request.user
        good_id = request.data.get("good_id")
        try:
            goods = store_models.Goods.objects.get(id=good_id)
        except store_models.Goods.DoesNotExist:
            return Response({"status": False, "code": 404})
        
        favorite_qs = models.UserFavorite.objects.filter(user=user, goods=goods)
        if not favorite_qs.exists():
            return Response({"status": False, "code": 400})
        favorite_qs.first().delete()  # Викликаємо метод delete()
        return Response({"status": True})


class UserHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest):
        user = request.user
        history_items = user.goods_history.all()
        data = {
            "count": history_items.count(),
            "goods": [
                item.goods.as_mini_dict(
                    fields=["poster", "slug", "title", "price", "views_count", "date_published", "store"]
                )
                for item in history_items
            ]
        }
        return Response(data)


class UserCartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cart_items = user.cart.all()  # отримуємо всі записи кошика для користувача
        total_sum = Decimal("0.00")
        total_quantity = 0

        items = []
        for item in cart_items:
            price = item.goods.price if item.goods and item.goods.price is not None else Decimal("0.00")
            total_sum += price * item.quantity
            total_quantity += item.quantity
            goods_data = item.goods.as_mini_dict(
                fields=["id", "slug", "poster",  "title", "price", "views_count", "date_published", "store"]
            )
            goods_data["quantity"] = item.quantity
            items.append(goods_data)

        data = {
            "items_count": cart_items.count(),
            "total_sum": str(total_sum),
            "goods": items
        }
        return Response(data)

    def post(self, request):
        user = request.user
        good_id = request.data.get("good_id")
        try:
            goods = store_models.Goods.objects.get(pk=good_id)
        except store_models.Goods.DoesNotExist:
            return Response({"status": False, "code": 404})
        
        add_quantity = 1

        # Якщо товар уже є в кошику – збільшуємо його quantity, інакше створюємо новий запис
        cart_item, created = models.UserCart.objects.get_or_create(
            user=user,
            goods=goods,
            defaults={"quantity": add_quantity}
        )
        if not created:
            cart_item.quantity += add_quantity
            cart_item.save()

        # Обчислюємо оновлену сумарну вартість
        cart_items = models.UserCart.objects.filter(user=user)
        total_sum = sum(
            item.goods.price * item.quantity
            for item in cart_items
            if item.goods and item.goods.price is not None
        )
        total_sum = str(total_sum)

        return Response({
            "status": True,
            "quantity": cart_item.quantity,
            "total_sum": total_sum
        })

    def delete(self, request):
        user = request.user
        good_id = request.data.get("good_id")
        try:
            goods = store_models.Goods.objects.get(pk=good_id)
        except store_models.Goods.DoesNotExist:
            return Response({"status": False, "code": 404})
        
        remove_quantity = 1
        cart_item_qs = models.UserCart.objects.filter(user=user, goods=goods)
        if not cart_item_qs.exists():
            return Response({"status": False, "code": 400})
        quantity = 0
        cart_item = cart_item_qs.first()
        if cart_item.quantity > remove_quantity:
            cart_item.quantity -= remove_quantity
            cart_item.save()
            quantity = cart_item.quantity
        else:
            cart_item.delete()
        
        # Обчислюємо оновлену сумарну вартість після змін
        cart_items = models.UserCart.objects.filter(user=user)
        total_sum = sum(
            item.goods.price * item.quantity
            for item in cart_items
            if item.goods and item.goods.price is not None
        )
        total_sum = str(total_sum)
        return Response({
            "status": True,
            "total_sum": total_sum,
            "quantity": quantity,
        })


class UserLogout(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            auth_logout_user(request)
            return Response({"status": True})
        return Response({"status": False, "message": "User not authenticated"})



class UserCsrf(APIView):
    def get(self, request):
        token = get_token(request)
        return Response({"csrf_token": token})
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token не наданий"}, status=status.HTTP_400_BAD_REQUEST)
        session_token = get_token(request)
        if token == session_token:
            token_status = True
        else:
            token_status = False
        return Response({
            "status": token_status,
        })