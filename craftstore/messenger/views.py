from rest_framework.views import APIView
from rest_framework.response import Response
from modules import serializers, filters, datetimeutils
from user.utils import get_user_by_request
from . import models
from django.utils.dateparse import parse_datetime


class UserChatSet(APIView):
    def get(self, request):
        user = get_user_by_request(request=request)
        if not user:
            return Response({"status": False, "code": 400})
        model = models.Chat
        queryset = filters.object_filter(request=request, object=model.objects.all())
        serializer = serializers.get_serializer_for_model(
            queryset=queryset,
            model=model,
            fields=["slug", "date"]
        )
        data = serializer.data
        return Response(data)


class ChatMessageSet(APIView):
    def get(self, request, slug):
        user = get_user_by_request(request)
        if not models.Chat.objects.filter(slug=slug).exists():
            return Response({"status": False, "message": "Chat undefined"})
        if not user:
            return Response({"status": False, "message": "User undefined"})
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
