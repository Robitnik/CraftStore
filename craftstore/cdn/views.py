from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpRequest
from user.utils import get_user_by_request
from modules.files import save_uploaded_file
from cdn.utils import image_to_cloud
from . import models
from django.utils.decorators import method_decorator
from modules.decorators.user_decorators import user_required
from django.views.decorators.csrf import csrf_exempt


class ImageSet(APIView):
    @method_decorator(user_required, name='dispatch')
    def post(self, request: HttpRequest):
        url = request.data.get("path")
        if not url:
            return Response({"error": "Path is required"}, status=400)
        url = f"images/{url}"
        uploaded_file = request.FILES.get("image")
        if not uploaded_file:
            return Response({"error": "Image file is required"}, status=400)
        img = image_to_cloud(save_uploaded_file(uploaded_file), url=url)
        data = img.as_mini_dict()
        data["status"] = True
        return Response(data)
    @method_decorator(user_required, name='dispatch')
    def delete(self, request: HttpRequest):
        user = request.user
        img_id = request.data.get("id")
        if not models.Image.objects.filter(pk=img_id).exists():
            return Response({"status": False, "code": 404}, status=404)
        img_obj = models.Image.objects.get(pk=img_id)
        if user != img_obj.author:
            return Response({"status": False, "code": 404, "message": "This user dont have premission to this image."})
        status, message = img_obj.delete()
        return Response({"status": status, "message": message})