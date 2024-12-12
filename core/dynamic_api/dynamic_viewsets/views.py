from rest_framework import viewsets
from ..dynamic_serializers.views import DynamicSerializer

class DynamicViewSet(viewsets.ModelViewSet):
    """ 
    dynamically generates a viewset for any  model,  allowing CRUD operations.
    """
    def __init__(self, model, *args, **kwargs):
        self.model = model
        self.serializer_class = DynamicSerializer(model).create_serializer()
        self.queryset = model.objects.all()
        super().__init__(*args, **kwargs)
        
        
""" 
modelname_viewset = DynamicViewSet(model=modelname)
This setup allows DynamicViewSet to automatically create endpoints with CRUD functionality for any model, 
enabling scalable and dynamic API development without the need for individual viewset classes for each model.
"""