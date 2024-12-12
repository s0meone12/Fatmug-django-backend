from rest_framework import serializers

class DynamicSerializer:
    """ 
    This class generates a serializer for any model, mapping all fields
    takes a model as input and returns a serializer for it.
    """
    
    def __init__(self, model):
        self.model = model

    def create_serializer(self):
        # Define a Meta class with the model and fields
        Meta = type('Meta', (object,), {'model': self.model, 'fields': '__all__'})
        # Create the serializer class dynamically
        serializer_class = type(f'{self.model.__name__}Serializer', (serializers.ModelSerializer,), {'Meta': Meta})
        return serializer_class
