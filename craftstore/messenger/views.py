from django.core.paginator import Paginator, EmptyPage
from collections import OrderedDict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from user.models import User
from modules import filters
from . import models
from . import utils


class UserChatSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest):
        user = request.user
        chats = models.Chat.objects.filter(members=user)
        chats = chats.annotate(last_message_date=Max('messages__send_date')).order_by('-last_message_date')
        chats = filters.object_filter(request=request, queryset=chats)
        data = {"count": chats.count(), "chats": []}
        for chat in chats:
            chat_dict = chat.as_dict()
            chat_dict["opponent"] = chat.get_chat_user(request.user).as_mini_dict()
            chat_dict["last_message"] = chat.get_last_message()
            chat_dict["unread_message_count"] = chat.get_unread_message_count()
            data["chats"].append(chat_dict)
        
        return Response(data)

    def post(self, request: HttpRequest):
        # Отримуємо opponent_id з даних запиту
        opponent_id = request.data.get("oponent_id")
        if not opponent_id:
            return Response({"error": "Параметр 'oponent_id' обов'язковий."}, status=400)

        try:
            opponent = User.objects.get(id=opponent_id)
        except User.DoesNotExist:
            return Response({"error": "Опонент не знайдений."}, status=404)

        # Перевіряємо, чи існує чат між поточним користувачем та опонентом
        chat = utils.get_chat_between_users(request.user, opponent)
        if not chat:
            chat = models.Chat.objects.create()
            chat.members.add(request.user, opponent)
            chat.save()

        data = chat.as_dict()
        # Використовуємо метод get_chat_user для отримання співрозмовника
        opponent_obj = chat.get_chat_user(request.user)
        data["opponent"] = opponent_obj.as_mini_dict() if opponent_obj else None
        return Response(data)


class ChatMessageSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest, username):
        if not User.objects.filter(username=username).exists():
            return Response({"status": False, "message": "Chat undefined"})
        chat = utils.get_chat_between_users(request.user, User.objects.get(username=username))
        data = chat.as_dict()
        data["opponent"] = chat.get_chat_user(request.user).as_mini_dict()
        data["unread_message_count"] = chat.get_unread_message_count()
        return Response(data)


    def post(self, request: HttpRequest, username):
        # Отримання користувача-опонента
        try:
            opponent = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"status": False, "message": "User not found"}, status=404)

        # Отримання чату між користувачами
        chat = utils.get_chat_between_users(request.user, opponent)
        if not chat:
            return Response({"status": False, "message": "Chat not found"}, status=404)

        # Отримання параметрів пагінації з POST-запиту
        page = int(request.POST.get('page', 1))
        limit = 25

        messages_qs = chat.messages.all().order_by('send_date')
        paginator = Paginator(messages_qs, limit)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            return Response({"status": False, "message": "Invalid page"}, status=404)

        grouped_messages = OrderedDict()
        for message in page_obj:
            date_key = message.send_date.strftime('%Y-%m-%d')
            if date_key not in grouped_messages:
                grouped_messages[date_key] = []
            message_data = message.as_dict()
            message_data["sender"] = message.sender.as_mini_dict()
            grouped_messages[date_key].append(message_data)

        # Формуємо список даних з групуванням за датою
        data = []
        for date_str, messages in grouped_messages.items():
            data.append({
                "date": date_str,
                "messages": messages
            })

        # Формування інформації про пагінатор
        paginator_data = {
            "current_page": page_obj.number,
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "prev_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "has_next": page_obj.has_next(),
            "has_prev": page_obj.has_previous(),
        }

        response_data = {
            "data": data,
            "paginator": paginator_data,
        }
        return Response(response_data)


class UserSet(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request: HttpRequest):
        data = {"status": True, "list": []}
        username = request.data.get('username')
        if not username:
            return Response({"status": False, "message": "Username is required"})
        if len(username) <= 2:
            return Response({"status": False, "message": "Логін має бути більше 2 букв"})
        users = User.objects.filter(username__icontains=username)
        for user in users:
            user_data = user.as_mini_dict()
            chat = utils.get_chat_between_users(request.user, user)
            if chat:
                user_data["chat"] = chat.as_mini_dict()
            data["list"].append(user_data)
        return Response(data)