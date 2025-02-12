CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Чтобы cookie не были доступны из JS, нужен атрибут HttpOnly
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True


CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']


# Когда приложение заимеет production окружение и https соединение
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CORS_ALLOWED_ORIGINS = [
   "https://lv6xwh7d-3000.euw.devtunnels.ms",
   "http://localhost",
   "http://127.0.0.1"
]
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
