from rest_framework import serializers



class UniversalSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(UniversalSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        # Динамічна обробка ForeignKey та ManyToMany
        for field_name, field in self.fields.items():
            if isinstance(field, serializers.PrimaryKeyRelatedField):
                related_model = field.queryset.model
                related_serializer = self.get_related_serializer(related_model, field_name)
                self.fields[field_name] = related_serializer

            elif isinstance(field, serializers.ManyRelatedField):
                related_model = field.child_relation.queryset.model
                related_serializer = self.get_related_serializer(related_model, field_name, many=True)
                self.fields[field_name] = related_serializer

    def get_related_serializer(self, model, field_name, many=False):
        """
        Створює динамічний серіалізатор для ForeignKey або ManyToMany з конкретними полями.
        """
        field_spec = self.context.get('fields', {}).get(field_name, None)
        
        if field_spec:
            # Розбір складених полів, якщо є
            fields = [f.strip() for f in field_spec.split(',')]
        else:
            # Якщо немає специфікації, серіалізуємо все
            fields = '__all__'
        
        # Створюємо динамічний серіалізатор для переданої моделі з конкретними полями
        DynamicRelatedSerializer = type(f"{model.__name__}Serializer", (serializers.ModelSerializer,), {
            'Meta': type('Meta', (object,), {'model': model, 'fields': fields})
        })
        
        return DynamicRelatedSerializer(many=many)


def get_serializer_for_model(queryset, model, fields=None, many=True, context=None):
    DynamicSerializer = type(f"{model.__name__}Serializer", (UniversalSerializer,), {
        'Meta': type('Meta', (object,), {'model': model, 'fields': fields if fields else '__all__'})
    })
    
    return DynamicSerializer(queryset, many=many, context=context)


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