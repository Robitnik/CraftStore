from functools import wraps
from rest_framework.response import Response
from user.utils import get_user_by_request


def user_required(view_func):
    """
    Декоратор для REST API, який перевіряє наявність користувача, витягнутого кастомною функцією з заголовків.
    Якщо користувач не знайдений, повертає JSON-відповідь із кодом 401.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = get_user_by_request(request)
        if not user:
            return Response({"error": "Authentication required.", "code": 401}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view