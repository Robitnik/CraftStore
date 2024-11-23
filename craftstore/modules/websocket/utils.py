from urllib.parse import parse_qs

def parse_scope(scope):
    headers = {
        key.decode(): value.decode()
        for key, value in scope.get("headers", [])
    }
    query_params = parse_qs(scope.get("query_string", b"").decode())
    path = scope.get("path", "")
    user = scope.get("user", None)
    result = {
        "headers": headers,  # Заголовки
        "query_params": query_params,  # GET-параметри
        "path": path,  # Шлях запиту
        "user": user,  # Користувач (може бути анонімним)
    }

    return result