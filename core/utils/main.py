from django.apps import apps
import re
import pandas as pd
from django.db import models
import pytz
from django.conf import settings
from aiolimiter import AsyncLimiter


# Returns a model class for a given model name


class Utils:

    def camel_to_snake(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def convert_date_to_server_timezone(date):
        return date.astimezone(pytz.timezone(settings.TIME_ZONE))

    


def get_model(model_name):
    return apps.get_model('core', model_name)

# Returns a list of field names for a given model class


def clean_choice_fields(df, model_class):
    # Iterate through fields in the model
    for field in model_class._meta.get_fields():
        # Check if the field has choices
        if hasattr(field, 'choices') and field.choices:
            # Get the valid choices for the field
            valid_choices = {choice[0] for choice in field.choices}

            # Check if the field exists in the DataFrame
            if field.name in df.columns:
                # Convert all values in the DataFrame column to lowercase
                df[field.name] = df_values = df[field.name].str.lower()

                # Check if all values are part of the valid choices
                invalid_values = df_values[~df_values.isin(valid_choices)]

                if not invalid_values.empty:
                    raise Exception(
                        f'Invalid values found in column {field.name}: {invalid_values.unique()}')

    return df


def check_n_update_df_as_per_model(df, model_class, is_subset=False):

    # Convert columns to snake case if a conversion function is provided
    df.rename(columns=camel_to_snake, inplace=True)

    # Check if dataframe columns match the model fields
    model_fields_1 = get_list_of_model_field_names(
        model_class, exclude_field_names=['id'])
    df_columns = set(df.columns)
    model_fields_set_1 = set(model_fields_1)

    # Rename foreign key fields in df to match the model

    model_fields_set_2 = []

    for field_name in model_fields_1:
        field = model_class._meta.get_field(field_name)
        if field.get_internal_type() == 'ForeignKey':
            field_name = field.name + '_id'
        model_fields_set_2.append(field_name)

    model_fields_set_2 = set(model_fields_set_2)

    if is_subset and not (model_fields_set_1.issubset(df_columns) or model_fields_set_2.issubset(df_columns)):
        raise Exception('Columns in df are not a subset of model fields: {} vs {}, {} vs {}'.format(
            model_fields_set_1.difference(
                df_columns), df_columns.difference(model_fields_set_1),
            model_fields_set_2.difference(df_columns), df_columns.difference(model_fields_set_2)))
    elif not is_subset and not (model_fields_set_1 == df_columns or model_fields_set_2 == df_columns):
        raise Exception('Columns in df do not match model fields: {} vs {}, {} vs {}'.format(
            model_fields_set_1.difference(
                df_columns), df_columns.difference(model_fields_set_1),
            model_fields_set_2.difference(df_columns), df_columns.difference(model_fields_set_2)))

    # Field type to Pandas dtype mapping
    field_to_dtype = {
        'ForeignKey': 'Int64',
        'IntegerField': 'Int64',
        'FloatField': 'float64',
        'BooleanField': 'bool',
        'DateTimeField': lambda x: pd.to_datetime(x),
        'DateField': lambda x: pd.to_datetime(x).dt.date,
        'CharField': 'str',
        'TextField': 'str',
        'DurationField': lambda x: pd.to_timedelta(x),
        'DecimalField': 'float64',
        'PositiveIntegerField': 'Int64',
        'PositiveSmallIntegerField': 'Int64',
        'BigIntegerField': 'Int64',
        'SmallIntegerField': 'Int64',
        'AutoField': 'Int64',
        'BigAutoField': 'Int64',
        'EmailField': 'str',
        'URLField': 'str',
        'FileField': 'str',
        'ImageField': 'str',
        'UUIDField': 'str',
        'BinaryField': 'bytes'
    }

    for field_name in df.columns:
        field_type = model_class._meta.get_field(
            field_name).get_internal_type()
        conversion = field_to_dtype.get(field_type)

        if not conversion:
            raise Exception(f'Field type {field_type} not supported')

        if callable(conversion):
            df[field_name] = conversion(df[field_name])
        else:
            df[field_name] = df[field_name].astype(conversion)

    df = clean_choice_fields(df, model_class)

    return df


def rename_foreign_field_in_df_to_insert(df, model_class):
    for field in model_class._meta.fields:
        if field.get_internal_type() == 'ForeignKey':
            field_name = field.name
            if field_name in df.columns:
                df.rename(
                    columns={field.name: field.name + '_id'}, inplace=True)
    return df


def clean_df_before_insert(df, model_class):
    df = rename_foreign_field_in_df_to_insert(df, model_class)

    # Identify fields from the model and their types
    model_fields = {field.name: field for field in model_class._meta.fields}

    for column in df.columns:
        if column in model_fields:
            field = model_fields[column]

            # Handle DateTimeField and DateField
            if isinstance(field, (models.DateTimeField, models.DateField)):
                df[column] = df[column].where(pd.notna(df[column]), None)

            # Handle FloatField and DecimalField
            elif isinstance(field, (models.FloatField, models.DecimalField)):
                default_value = field.default if field.default != models.NOT_PROVIDED else None
                if default_value is not None:
                    df[column] = df[column].fillna(default_value).astype(
                        'float64')
                else:
                    # Handle the case where default_value is None, maybe fill with 0, or use another method
                    df[column] = df[column].fillna(0).astype('float64')

            # Handle IntegerFields
            elif isinstance(field, (
                    models.IntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField,
                    models.BigIntegerField, models.SmallIntegerField)):
                default_value = field.default if field.default != models.NOT_PROVIDED else None
                if default_value is None:
                    # Handle the case where default_value is None, maybe fill with 0, or use another method
                    df[column] = df[column].fillna(0).astype('Int64')
                else:
                    df[column] = df[column].fillna(default_value).astype(
                        'Int64')  # Use 'Int64' to keep NaN as <NA>

            # Handle CharField and TextField
            elif isinstance(field, (models.CharField, models.TextField)):
                default_value = field.default if field.default != models.NOT_PROVIDED else ''
                df[column] = df[column].fillna(default_value)

            # Handle BooleanField (Note: Assumes False for NaN. Adjust if needed.)
            elif isinstance(field, models.BooleanField):
                df[column] = df[column].fillna(False)

            # ... You can continue for other field types if needed

    return df


def get_rate_limiter(max_rate: int, request_per_second: float) -> AsyncLimiter:
    time_per_request = 1 / request_per_second  # 1 request per 59.88 seconds
    time_period = max_rate * time_per_request  # 15 requests per 898.2 seconds
    # max_rate / time_period => 15 / 898.2 = 0.0167000668002672, So Rate (requests per second) is 0.0167
    return AsyncLimiter(max_rate=max_rate, time_period=time_period)
