from django.db.models import Q


def object_filter(request, object, order=None, blockeys=None, manytomany=None):
    if not blockeys:
        blockeys = ["order", "limit", "page"]
    if not manytomany:
        manytomany = []

    order = request.GET.get("order_by", order)

    params_list = []
    model_fields = {field.name for field in object.model._meta.get_fields()}

    for key, value in request.GET.items():
        if key in blockeys:
            continue
        if key in model_fields or "__" in key:
            if value.lower() == "true":
                params_list.append([key, True])
            elif value.lower() == "false":
                params_list.append([key, False])
            else:
                if "," in value:
                    values = value.split(",")
                    for new_value in values:
                        params_list.append([key, new_value])
                elif "-" in value:
                    values = value.split("-")
                    if len(values) == 2 and values[0].isdigit() and values[1].isdigit():
                        for new_value in range(int(values[0]), int(values[1]) + 1):
                            params_list.append([key, new_value])
                else:
                    params_list.append([key, value])

    filters = Q()

    for field_name, field_value in params_list:
        if "__" in field_name:
            filters |= Q(**{field_name: field_value})
        elif field_name in manytomany:
            filters |= Q(**{f"{field_name}__pk__in": [field_value]})
        else:
            filters |= Q(**{f"{field_name}__icontains": field_value})

    object = object.filter(filters)

    if order:
        object = object.order_by(order)

    if manytomany:
        object = object.distinct()

    return object
