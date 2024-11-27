import time
from django.db import connection, reset_queries

class QueryLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        reset_queries()
        start_time = time.time()
        response = self.get_response(request)
        total_time = time.time() - start_time
        queries = connection.queries

        print("\n--- Запити до бази даних ---")
        for query in queries:
            print(f"{query['sql']}\nЧас виконання: {query['time']} сек")

        print(f"\nЗагальна кількість запитів: {len(queries)}")
        print(f"Час обробки запитів: {total_time:.2f} сек\n")

        return response