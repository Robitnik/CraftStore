from . import models
from modules.filters import object_filter
from django.core.paginator import Paginator, EmptyPage
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
    permission_classes = []
    def get(self, request, *args, **kwargs):
        model = models.Goods
        queryset = object_filter(request=request, queryset=model.objects.all(), order=request.GET.get("order_by", "-date_published"))
        data = []
        for good in queryset:
            good_data = good.as_mini_dict(fields=["id", "title", "slug", "price", "views_count", "description", "date_published", "date_updated"])
            if request.user.is_authenticated:
                good_data["user"] = good.user_info(request.user)
            data.append(good_data)
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
        queryset = object_filter(request=request, queryset=models.Store.objects.all())
        serializer = serializers.get_serializer_for_model(
            queryset=queryset,
            model=model,
            fields=['store', 'slug', 'title', 'price', 'poster', 'description', 'views_count', 'bought_count', 'published', 'count', 'date_published', 'date_updated']
        )
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)


class StoreGoodSet(APIView):
    def get(self, request: HttpRequest, goods_id=None):
        # Повна інформація.
        if not goods_id:
            return Response({"status": False, "code": 404}, status=404)
        goods = models.Goods.objects.filter(pk=goods_id)
        if not goods.exists():
            return Response({"status": False, "code": 404}, status=404)
        goods = models.Goods.objects.get(pk=goods_id)
        data = goods.as_dict()
        if request.user.is_authenticated:
            data["user"] = goods.user_info(request.user)
        return Response(data)
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
            queryset = object_filter(request=request, queryset=models.Category.objects.all())
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



class GoodsReviewViewSet(APIView):
    def get(self, request: HttpRequest, goods_id):
        if not models.Goods.objects.filter(pk=goods_id).exists():
            return Response({"status": False, "code": 404}, status=404)
        goods = models.Goods.objects.get(pk=goods_id)
        main_reviews = goods.reviews.filter(parent__isnull=True)
        paginator = Paginator(main_reviews, 20)
        page = request.GET.get("page", 1)
        try:
            reviews_page = paginator.page(page)
        except EmptyPage:
            reviews_page = paginator.page(paginator.num_pages)
        
        review_data = [review.as_dict() for review in reviews_page]
        data = {
            "current_page": reviews_page.number,
            "next_page": reviews_page.next_page_number() if reviews_page.has_next() else None,
            "prev_page": reviews_page.previous_page_number() if reviews_page.has_previous() else None,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "has_next": reviews_page.has_next(),
            "has_prev": reviews_page.has_previous(),
            "results": review_data
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest, goods_id):
        if not models.Goods.objects.filter(pk=goods_id).exists():
            return Response({"status": False, "code": 404}, status=404)
        goods = models.Goods.objects.get(pk=goods_id)
        text = request.data.get("text")
        rating = request.data.get("rating")
        parent_review_id = request.data.get("parent_review_id")
        if not text or not rating:
            return Response({"status": False, "code": 400, "error": "Текст та оцінка обов'язкова"}, status=400)
        review = models.Review(text=text, rating=rating, goods=goods, user=request.user)
        if parent_review_id and models.Review.objects.filter(pk=parent_review_id).exists():
            parent_review = models.Review.objects.filter(pk=parent_review_id).first()
            if parent_review:
                review.parent = parent_review
        review.save()
        return Response({"status": True,  "review": review.as_dict()})


class ReviewViewSet(APIView):

    def get(self, request: HttpRequest, review_id):
        if not models.Review.objects.filter(pk=review_id).exists():
            return Response({"status": False, "code": 404}, status=404)
        review = models.Review.objects.get(pk=review_id)
        
        # Отримуємо всі відповіді для даного відгуку (гілку)
        replies = review.replies.all()
        # Налаштування пагінації: 10 відповідей на сторінці (можна змінити)
        paginator = Paginator(replies, 10)
        page = request.GET.get("page", 1)
        try:
            replies_page = paginator.page(page)
        except EmptyPage:
            replies_page = paginator.page(paginator.num_pages)
        
        data = {
            "current_page": replies_page.number,
            "next_page": replies_page.next_page_number() if replies_page.has_next() else None,
            "prev_page": replies_page.previous_page_number() if replies_page.has_previous() else None,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "has_next": replies_page.has_next(),
            "has_prev": replies_page.has_previous(),
            "replies": []
                }
        data["replies"] = [reply.as_dict() for reply in replies_page]
        return Response(data)


    def put(self, request: HttpRequest, review_id):
        if not models.Review.objects.filter(pk=review_id).exists():
            return Response({"status": False, "code": 404}, status=404)
        review = models.Review.objects.get(pk=review_id)
        if request.user != review.user:
            return Response({"status": False, "code": 403}, status=403)
        text = request.data.get("text")
        rating = request.data.get("rating")
        if not text and not rating:
            return Response({"status": False, "code": 400, "error": "Текст та оцінка обов'язкова"}, status=400)
        review.text = text
        review.rating = rating
        review.save()
        return Response({"status": True,  "review": review.as_dict()})


    def delete(self, request: HttpRequest, review_id):
        if not models.Review.objects.filter(pk=review_id).exists():
            return Response({"status": False, "code": 404}, status=404)
        review = models.Review.objects.get(pk=review_id)
        if request.user != review.user:
            return Response({"status": False, "code": 403}, status=403)
        review.delete()
        return Response({"status": True})