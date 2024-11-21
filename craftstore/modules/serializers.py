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

    class Meta:
        model = None
        fields = '__all__'



def get_serializer_for_model(queryset, model, fields=None, many=True):
    Meta = type('Meta', (object,), {'model': model, 'fields': fields if fields else '__all__'})
    DynamicSerializer = type(
        'DynamicSerializer',
        (UniversalSerializer,),
        {'Meta': Meta}
    )
    return DynamicSerializer(queryset, many=many)



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