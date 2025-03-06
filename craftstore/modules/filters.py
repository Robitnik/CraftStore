from django.db.models import Q


def object_filter(request, queryset, order=None, blockeys=None, manytomany=None):
    if not blockeys:
        blockeys = ["order", "limit", "page"]
    if not manytomany:
        manytomany = []

    order = request.GET.get("order_by", order)

    params_list = []
    model_fields = {field.name for field in queryset.model._meta.get_fields()}

    for key, value in request.GET.items():
        if key in blockeys:
            continue
        if key in model_fields or "__" in key:
            if value.lower() == "true":
                params_list.append((key, True))
            elif value.lower() == "false":
                params_list.append((key, False))
            else:
                if "," in value:
                    # Якщо є декілька значень через кому, додаємо їх окремо
                    for new_value in value.split(","):
                        params_list.append((key, new_value.strip()))
                elif "-" in value:
                    # Для діапазону використовуємо __range lookup замість генерації окремих умов
                    values = value.split("-")
                    if len(values) == 2 and values[0].strip().isdigit() and values[1].strip().isdigit():
                        start, end = int(values[0].strip()), int(values[1].strip())
                        params_list.append((f"{key}__range", (start, end)))
                else:
                    params_list.append((key, value))

    # Комбінуємо фільтри через AND, щоб всі умови виконувались
    filters = Q()
    for field_name, field_value in params_list:
        if field_name.endswith("__range"):
            filters &= Q(**{field_name: field_value})
        elif "__" in field_name:
            filters &= Q(**{field_name: field_value})
        elif field_name in manytomany:
            filters &= Q(**{f"{field_name}__pk__in": [field_value]})
        else:
            filters &= Q(**{f"{field_name}__icontains": field_value})

    queryset = queryset.filter(filters)

    if order:
        queryset = queryset.order_by(order)

    if manytomany:
        queryset = queryset.distinct()

    return queryset
