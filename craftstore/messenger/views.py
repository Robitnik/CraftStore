from rest_framework.views import APIView
from rest_framework.response import Response
from modules import serializers, filters
from user.utils import get_user_by_request
from . import models


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
