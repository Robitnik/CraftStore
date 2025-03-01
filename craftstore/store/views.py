from . import models
from modules.filters import object_filter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import HttpRequest
from rest_framework.permissions import IsAuthenticated
from modules import serializers
from django.http import HttpResponse
from .components import dbutils


class Test(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request: HttpRequest):
        goods1 = models.Goods.objects.get(pk=1)
        return Response(goods1.as_dict(fields=["title"]))

def main(request:HttpRequest):
    return  HttpResponse("Craftstore")


class GoodsViewFilter(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, *args, **kwargs):
        model = models.Goods
        queryset = object_filter(request=request, object=model.objects.all())
        data = []
        for good in queryset:
            data.append(good.as_mini_dict(fields=["id", "title", "slug", "price", "views_count", "description", "date_published", "date_updated"]))
        return Response(data, status=status.HTTP_200_OK)




class UserStore(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        queryset = models.Store.objects.filter(owner=user)
        if not queryset.exists():
            return Response({"status": False, "code": 404}, status=404)
        store = queryset.first()
        data = store.as_dict()
        return Response(data, status=status.HTTP_200_OK)


    def post(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        store = dbutils.UserStore(user=user)
        return Response(store.create_store(request=request))


    def delete(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        store = dbutils.UserStore(user=user)
        return Response(store.delete_store(request=request))


class StoreViewSet(APIView):
    authentication_classes = []
    permission_classes = []
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
    permission_classes = [IsAuthenticated]
    def get(self, request: HttpRequest):
        # товари магазину
        return Response({})
    def post(self, request: HttpRequest):
        user = request.user
        store = user.store
        good = dbutils.StoreGood(store=store, user=user)
        if "hide" in request.GET:
            data = good.hide_good(request=request)
        elif "unhide" in request.GET:
            data = good.unhide_good(request=request)
        elif "create" in request.GET:
            data = good.add_good(request=request)
        else:
            data = {"status": False, "code": 404}
        return Response(data)

    def put(self, request: HttpRequest):
        user = request.user
        store = user.store
        good = dbutils.StoreGood(store=store, user=user)
        return Response(good.update_good(request=request))
    def delete(self, request: HttpRequest):
        user = request.user
        store = user.store
        good = dbutils.StoreGood(store=store, user=user)
        return Response(good.delete_good(request=request))


class GoodsViewSet(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request: HttpRequest, store_slug, goods_slug):
        if not  models.Goods.objects.filter(slug=goods_slug).exists():
            return Response({"status": False, "code": 404}, status=404)
        goods = models.Goods.objects.get(slug=goods_slug)
        return Response(goods.as_dict())


class CategoryViewSet(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request: HttpRequest, *args, **kwargs):
        if request.GET.get("id") and isinstance(request.GET.get("id"), int):
            queryset = models.Category.objects.filter(pk=request.GET.get("id"))
        else:
            queryset = object_filter(request=request, object=models.Category.objects.all())
        data = {"count": queryset.count(), "results": []}
        if not queryset.exists():
            return Response({"status": False, "code": 404}, status=404)
        if queryset.count() == 1:
            category = queryset.first()
            category_data = category.as_dict()
            if category.sub_categories and category.sub_categories.count() > 0:
                category_data["sub_categories"] = [sub.as_mini_dict() for sub in category.sub_categories.all()]
            data["results"] = [category_data]
            return Response(data)
        for category in queryset:
            data["results"].append(category.as_dict())
        return Response(data, status=status.HTTP_200_OK)