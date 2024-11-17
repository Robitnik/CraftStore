from django.db.models import Q


def object_filter(request, object, order=None, blockeys=["order", "limit", "page"], manytomany=[]):
    if not order and request.GET.get('order'):
        order = request.GET.get('order')
    params_list = []
    model_fields = [field.name for field in object.model._meta.get_fields()]

    for key, value in request.GET.items():
        if key in model_fields:
            if key in blockeys:
                continue
            if key == "id":
                params_list.append(["pk", value])
            elif key == "mal_id":
                params_list.append(["mall_id", value])
            else:
                if "," in value:
                    values = value.split(",")
                    for new_value in values:
                        params_list.append([key, new_value])
                elif "-" in value:
                    values = value.split("-")
                    if len(values) > 1:
                        for new_value in range(int(values[0]), int(values[1]) + 1):
                            params_list.append([key, new_value])
                else:
                    params_list.append([key, value])

    filters = Q()

    for i in params_list:
        field_name = i[0]
        field_value = i[1]
        if field_name in manytomany:
            filters |= Q(**{f"{field_name}__pk__in": [field_value]})
        else:
            filters |= Q(**{f"{field_name}__icontains": field_value})
    if order:
        object = object.filter(filters).order_by(order)
    else:
        object = object.filter(filters)
    return object
