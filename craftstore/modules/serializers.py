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