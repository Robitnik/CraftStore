from rest_framework import serializers


class UniversalSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(UniversalSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            parsed_fields = self.parse_fields(fields)
            self.filter_fields(parsed_fields)

    def parse_fields(self, fields):
        """
        Перетворює список полів у форматі ['field[subfield1,subfield2]', ...] 
        у вкладену структуру словника.
        """
        parsed = {}
        for field in fields:
            if "[" in field and "]" in field:
                main_field, nested_fields = field.split("[", 1)
                nested_fields = nested_fields.rstrip("]").split(",")
                parsed[main_field] = nested_fields
            else:
                parsed[field] = None
        return parsed

    def filter_fields(self, parsed_fields):
        """
        Фільтрує поля серіалізатора на основі вкладеної структури.
        """
        allowed = set(parsed_fields.keys())
        existing = set(self.fields.keys())

        # Видаляємо непотрібні поля
        for field_name in existing - allowed:
            self.fields.pop(field_name)

        # Обробляємо вкладені поля
        for field_name, nested_fields in parsed_fields.items():
            if nested_fields is not None:
                field = self.fields[field_name]
                if isinstance(field, serializers.PrimaryKeyRelatedField):
                    related_model = field.queryset.model
                    self.fields[field_name] = self.get_related_serializer(
                        related_model, nested_fields, many=False
                    )
                elif isinstance(field, serializers.ManyRelatedField):
                    related_model = field.child_relation.queryset.model
                    self.fields[field_name] = self.get_related_serializer(
                        related_model, nested_fields, many=True
                    )

    def get_related_serializer(self, model, fields, many=False):
        """
        Створює серіалізатор для реляційних полів із вкладеними підполями.
        """
        DynamicRelatedSerializer = type(
            f"{model.__name__}Serializer",
            (serializers.ModelSerializer,),
            {
                'Meta': type('Meta', (object,), {'model': model, 'fields': fields})
            }
        )
        return DynamicRelatedSerializer(many=many)


def get_serializer_for_model(queryset, model, fields=None, many=True):
    """
    Генерує серіалізатор для моделі з визначеними полями.
    """
    DynamicSerializer = type(
        f"{model.__name__}Serializer",
        (UniversalSerializer,),
        {
            'Meta': type('Meta', (object,), {'model': model, 'fields': '__all__'})
        }
    )
    return DynamicSerializer(queryset, many=many, fields=fields)



class UniversalCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)
        fields = kwargs.pop('fields', None)
        if not model or not fields:
            raise ValueError("Параметри 'model' та 'fields' є обов'язковими.")
        super().__init__(*args, **kwargs)
    class Meta:
        model = None
        fields = '__all__'


def create_object(data, model, fields):
    serializer = UniversalCreateSerializer(
        data=data,
        model=model,
        fields=fields
    )
    if serializer.is_valid():
        return serializer.save()
    else:
        return serializer.errors