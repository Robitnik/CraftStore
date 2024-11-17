from . import models
from modules.filters import object_filter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Goods
from modules import serializers
from django.http import HttpResponse


def main(request):
    return  HttpResponse("Craftstore")


class GoodsViewSet(APIView):
    def get(self, request, *args, **kwargs):
        model = Goods
        queryset = object_filter(request=request, object=model.objects.all())
        
        serializer = serializers.get_serializer_for_model(
            queryset=queryset,
            model=model,
            fields=['store', 'slug', 'title', 'price', 'poster', 'description', 'views_count', 'bought_count', 'published', 'count', 'date_published', 'date_updated']
        )
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)