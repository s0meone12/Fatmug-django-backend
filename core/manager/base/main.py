import inspect
from functools import wraps
import pandas as pd
from django.db import models
from django.db.models.query import QuerySet
from .df_db_handler import DFDbHandler
from django.core.exceptions import FieldDoesNotExist


class CheckQSMeta(type):
    def __new__(mcs, name, bases, attrs):
        new_attrs = {}
        # if "get_qs" not in attrs.keys():
        #     raise ValueError(
        #         "get_qs method must be provided for the manager: %s" % name)
        for attr_name, attr_value in attrs.items():
            if callable(attr_value):
                sig = inspect.signature(attr_value)
                if "qs" in sig.parameters:
                    new_attrs[attr_name] = mcs.check_qs(attr_value)
                else:
                    new_attrs[attr_name] = attr_value
            else:
                new_attrs[attr_name] = attr_value
        return super().__new__(mcs, name, bases, new_attrs)

    @staticmethod
    def check_qs(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if len(args) > 1 or (args and isinstance(args[0], QuerySet)):
                raise ValueError(
                    "QuerySet must be passed as a keyword argument named 'qs'")
            qs = kwargs.get("qs")
            if qs is None:
                qs = self.model.objects.all()
            if isinstance(qs, self.model):
                qs = self.model.objects.filter(id=qs.id)
            elif not isinstance(qs, QuerySet) or qs.model != self.model:
                raise ValueError(
                    f"qs must be a QuerySet or instance of {self.model.__name__}"
                )
            kwargs["qs"] = qs
            return func(self, *args, **kwargs)
        return wrapper


class BaseQuerySet(models.QuerySet):
    # Add custom queryset functions here
    def to_verbose_df(self, fields: list | None = None):
        model = self.model
        fields_to_select = []

        if fields and isinstance(fields, list):
            selected_fields = fields
        elif not fields:
            selected_fields = [field.name for field in model._meta.fields]
        else:
            raise ValueError("fields must be a list of field names")

        # Identify foreign key fields and construct fields to select
        for field_name in selected_fields:
            try:
                field = model._meta.get_field(field_name)
                if isinstance(field, models.ForeignKey):
                    related_model = field.related_model
                    kn_name_field = getattr(
                        related_model, "KN_NAME_FIELD", "name")
                    if hasattr(related_model, kn_name_field):
                        fields_to_select.append(
                            f"{field.name}__{kn_name_field}")
                    elif hasattr(related_model, "name"):
                        fields_to_select.append(f"{field.name}__name")
                    else:
                        raise ValueError(
                            f"Data insufficiency: Neither 'KN_NAME_FIELD' nor 'name' found on related model {related_model.__name__}")
                else:
                    fields_to_select.append(field.name)
            except FieldDoesNotExist:
                raise ValueError(
                    f"Field '{field_name}' does not exist on model '{model.__name__}'")

        return self.to_df(fields_to_select)

    def to_df(self, fields: list | None = None):
        if fields and isinstance(fields, list):
            data = list(self.values(*fields))
        else:
            data = list(self.values())
        return pd.DataFrame(data)


class BaseManager(models.Manager, metaclass=CheckQSMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dfdb = None

    def get_queryset(self):
        # To call function directly on queryset
        return BaseQuerySet(self.model, using=self._db)

    @property
    def dfdb(self):
        if not self.__dfdb:
            self.__dfdb = DFDbHandler(self.model)
        return self.__dfdb
