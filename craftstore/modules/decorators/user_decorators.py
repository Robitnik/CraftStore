from functools import wraps
from rest_framework.response import Response


def user_required(view_func):
    """
    Декоратор, що перевіряє, чи користувач автентифікований (через request.user).
    Якщо користувач не автентифікований, повертає 401.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            return Response(
                {"status": False, "error": "Authentication required.", "code": 401},
                status=401
            )
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view