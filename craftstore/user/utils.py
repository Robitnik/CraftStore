from django.contrib.sessions.models import Session
from .models import User
from rest_framework.authtoken.models import Token


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
    elif username:
        user = User.objects.filter(username=username).first()
    return user, its_me


def get_user_by_request(request):
    return request.user if request.user.is_authenticated else None


def get_user_by_session_key(session_key: str) -> User:
    user, _ = get_user(session_key=session_key)
    return user


def get_user_by_token(token_key: str) -> User:
    """
    Повертає користувача, якщо існує токен з заданим ключем.
    Використовує модель Token з DRF.
    """
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None
