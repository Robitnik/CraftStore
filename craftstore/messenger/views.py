from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from rest_framework.permissions import IsAuthenticated
from modules import serializers, filters, datetimeutils
from . import models
from django.utils.dateparse import parse_datetime
from django.db.models import Max


class UserChatSet(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest):
        user = request.user
        chats = models.Chat.objects.filter(members=user)
        chats = chats.annotate(last_message_date=Max('masseges__send_date')).order_by('-last_message_date')
        chats = filters.object_filter(request=request, object=chats)
        data = {"count": chats.count(), "chats": []}
        for chat in chats:
            chat_dict = chat.as_dict()
            chat_dict["opponent"] = None
            for member in chat.members.all():
                if user != member:
                    chat_dict["opponent"] = member.as_dict()            
            data["chats"].append(chat_dict)
        
        return Response(data)


class ChatMessageSet(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest, slug):
        if not models.Chat.objects.filter(slug=slug).exists():
            return Response({"status": False, "message": "Chat undefined"})
        chat = models.Chat.objects.get(slug=slug)
        date_str = request.GET.get("date", datetimeutils.get_today_date())
        if isinstance(date_str, str):
            date = parse_datetime(date_str) or datetimeutils.get_today_date()
        else:
            date = date_str
        queryset = chat.masseges.filter(send_date__date=date)
        messages = [m.as_dict() for m in queryset]
        data = messages
        return Response(data)
