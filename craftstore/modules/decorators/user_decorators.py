from functools import wraps
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from django.contrib.auth.models import AnonymousUser


def user_required(view_func):
    """
    Декоратор для REST API, який перевіряє наявність користувача, витягнутого кастомною функцією з заголовків.
    Якщо користувач не знайдений, повертає JSON-відповідь із кодом 401.
    """
    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if not request.user or type(request.user) == AnonymousUser:
            return Response({"status": False, "error": "Authentication required.", "code": 401}, status=401)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
