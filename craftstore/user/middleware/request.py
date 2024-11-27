from django.utils.deprecation import MiddlewareMixin
from user.utils import get_user_by_request


class UserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = get_user_by_request(request)
        request.user = user