from . import models
from modules.filters import object_filter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from modules import serializers
from django.http import HttpResponse, HttpRequest
from user.utils import get_user_by_request
from .components import dbutils


def main(request:HttpRequest):
    return  HttpResponse("Craftstore")


class GoodsViewSet(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        model = models.Goods
        queryset = object_filter(request=request, object=model.objects.all())
        serializer = serializers.get_serializer_for_model(
            queryset=queryset,
            model=model,
            fields=['store', 'slug', 'title', 'price', 'poster', 'description', 'views_count', 'bought_count', 'published', 'count', 'date_published', 'date_updated']
        )
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)



class UserStore(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        user = get_user_by_request(request=request)
        model = models.Goods
        queryset = models.Goods.objects.filter(owner=user)
        serializer = serializers.get_serializer_for_model(
            queryset=queryset,
            model=model,
            fields=['name', 'avatar', 'slug']
        )
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)
    def post(self, request: HttpRequest, *args, **kwargs):
        user = get_user_by_request(request=request)
        store = dbutils.UserStore(user=user)
        return Response(store.create_store(request=request))
    def delete(self, request: HttpRequest, *args, **kwargs):
        user = get_user_by_request(request=request)
        store = dbutils.UserStore(user=user)
        return Response(store.delete_store(request=request))


class StoreViewSet(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        model = models.Store
        queryset = object_filter(request=request, object=models.Store.objects.all())
        serializer = serializers.get_serializer_for_model(
            queryset=queryset,
            model=model,
            fields=['store', 'slug', 'title', 'price', 'poster', 'description', 'views_count', 'bought_count', 'published', 'count', 'date_published', 'date_updated']
        )
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)
