from django.contrib.sessions.models import Session
from .models import User


def get_user(session_key=None, username=None):
    its_me = False
    user = None
    if session_key:
        session = Session.objects.filter(session_key=session_key)
        if session.exists():
            session = session.first()
            session_data = session.get_decoded()
            uid = session_data.get('_auth_user_id')
            user = User.objects.get(id=uid)
            its_me = True
            user.update_activity()
    elif username:
        user = User.objects.filter(username=username).first()
    return user, its_me


def get_user_by_request(request):
    if request.user and request.user.is_authenticated:
        return request.user
    session_key = request.GET.get('token', str(request.headers.get("authorization")))
    user, its_me = get_user(session_key=session_key)
    return user