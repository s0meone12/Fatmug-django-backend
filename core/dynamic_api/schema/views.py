from django.apps import apps
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
import inspect
from types import BuiltinFunctionType, MethodType
from zoneinfo import ZoneInfo
import pytz

import pytz.zoneinfo

class SchemaView(APIView):
    
    def get(self, request):
        schema = {}
        # Iterate over all models
        for model in apps.get_models():
            model_name = model.__name__
            fields = {}
            methods = {}
            # Collect detailed field information
            for field in model._meta.get_fields():
                field_info = {
                    'field_type': str(field.get_internal_type()) if hasattr(field, 'get_internal_type') else 'RelatedField',
                    'max_length': getattr(field, 'max_length', None),
                    'null': getattr(field, 'null', None),
                    'blank': getattr(field, 'blank', None),
                    'choices': getattr(field, 'choices', None),
                }
                # Additional constraints for Integer and Decimal fields
                if isinstance(field, (models.IntegerField, models.DecimalField)):
                    field_info.update({
                        'min_value': getattr(field, 'min_value', None),
                        'max_value': getattr(field, 'max_value', None),
                        'decimal_places': getattr(field, 'decimal_places', None) if isinstance(field, models.DecimalField) else None,
                        'max_digits': getattr(field, 'max_digits', None) if isinstance(field, models.DecimalField) else None,
                    })
                # Handle relationship fields
                if field.is_relation:
                    field_info.update({
                        'related_model': field.related_model.__name__ if field.related_model else None,
                        'relation_type': type(field).__name__
                    })
                    fields[field.name] = field_info  
                else:
                    # Check if the field's default value is of type ZoneInfo
                    if isinstance(field.default, ZoneInfo):
                        field_info.update({"default": field.default.zone})
                        fields[field.name] = field_info  
                    # Check if the field's default value is a pytz timezone object
                    elif isinstance(field.default, pytz.BaseTzInfo):
                        field_info.update({"default" : str(field.default)})
                        fields[field.name] = field_info                    
            # Collect method information, including argument names
            for method_name in dir(model):
                method = getattr(model, method_name)
                # Skip built-in types, and only process user-defined methods
                if callable(method) and not method_name.startswith('_') and not isinstance(method, (BuiltinFunctionType, MethodType)):
                    try:
                        signature = inspect.signature(method)
                        args = list(signature.parameters.keys())
                        methods[method_name] = {
                            'args': args,
                            'doc': method.__doc__ or "No description available"
                        }
                    except ValueError:
                        # Skip methods that don't have a signature (e.g., built-in exceptions like `DoesNotExist`)
                        continue

            # Add the model schema to the overall schema
            schema[model_name] = {
                'fields': fields,
                'methods': methods,
            }

        return Response(schema)