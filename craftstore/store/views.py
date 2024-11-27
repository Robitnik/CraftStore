from . import models
from modules.filters import object_filter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import HttpRequest
from modules import serializers
from django.http import HttpResponse
from user.utils import get_user_by_request
from .components import dbutils
from modules.decorators.user import user_required

class Test(APIView):
    def get(self, request: HttpRequest):
        goods1 = models.Goods.objects.get(pk=1)
        return Response(goods1.as_dict(fields=["title"]))

def main(request:HttpRequest):
    return  HttpResponse("Craftstore")

class GoodsViewFilter(APIView):
    def get(self, request, *args, **kwargs):
        model = models.Goods
        queryset = object_filter(request=request, object=model.objects.all())
        data = []
        for good in queryset:
            data.append(good.as_mini_dict(fields=["poster", "slug", "title", "price", "views_count", "date_published", "store"]))
        return Response(data, status=status.HTTP_200_OK)




class UserStore(APIView):
    @user_required
    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        model = models.Goods
        queryset = models.Goods.objects.filter(owner=user)
        serializer = serializers.get_serializer_for_model(
            queryset=queryset,
            model=model,
            fields=['name', 'avatar', 'slug']
        )
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)
    @user_required
    def post(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        store = dbutils.UserStore(user=user)
        return Response(store.create_store(request=request))
    @user_required
    def delete(self, request: HttpRequest, *args, **kwargs):
        user = request.user
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


class StoreGoodSet(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        # товари магазину
        return Response({})
    @user_required
    def post(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        store = user.store
        good = dbutils.StoreGood(store=store, user=user)
        if "hide" in request.GET:
            data = good.hide_good(request=request)
        if "unhide" in request.GET:
            data = good.unhide_good(request=request)
        if "create" in request.GET:
            data =good.add_good(request=request)
        else:
            data = {"status": False, "code": 404}
        return Response(data)
    @user_required
    def put(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        store = user.store
        good = dbutils.StoreGood(store=store, user=user)
        return Response(good.update_good(request=request))
    @user_required
    def delete(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        store = user.store
        good = dbutils.StoreGood(store=store, user=user)
        return Response(good.delete_good(request=request))


class GoodsViewSet(APIView):
    def get(self, request: HttpRequest, store_slug, goods_slug):
        if not  models.Goods.objects.filter(slug=goods_slug).exists():
            return Response({"status": False, "code": 404}, status=404)
        goods = models.Goods.objects.get(slug=goods_slug)
        return Response(goods.as_dict())