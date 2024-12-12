import pandas as pd
from django.db import models, transaction
from core.utils import Utils
from datetime import datetime


class DFDbHandler:

    def __init__(self, model=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    def __get_unique_field_tuples(self, model=None):
        """
        Given a Django model class, return a list of tuples representing fields that, together, form a UNIQUE constraint.
        - Fields with `unique=True` are represented as tuples containing a single field name.
        - Fields listed in the `unique_together` tuple in the model's `Meta` class are represented as tuples.
        - For foreign key fields, add "_id" suffix to their names.
        """

        if model is None:
            model = self.model

        unique_field_tuples = []
        # Check fields with `unique=True` and add "_id" suffix for foreign keys
        for field in model._meta.fields:
            if field._unique:
                if isinstance(field, models.ForeignKey):
                    unique_field_tuples.append((field.name + "_id",))
                else:
                    unique_field_tuples.append((field.name,))
        # Check fields listed in `unique_together` tuple and add "_id" suffix for foreign keys
        if hasattr(model._meta, "unique_together"):
            unique_together_fields = model._meta.unique_together
            for fields in unique_together_fields:
                updated_fields = []
                for field in fields:
                    if isinstance(model._meta.get_field(field), models.ForeignKey):
                        updated_fields.append(field + "_id")
                    else:
                        updated_fields.append(field)
                unique_field_tuples.append(tuple(updated_fields))

        return unique_field_tuples

    def __get_editable_fields(self):
        """
        Given a Django model class, return a list of field names that are safely editable,
        excluding primary keys, unique constraints, non-editable fields, relations, and file fields.
        """

        model = self.model

        excluded_fields = set()
        # Exclude primary key field and other potential risky fields
        primary_key_field = model._meta.pk.name
        excluded_fields.add(primary_key_field)
        # Collecting fields to be considered as editable
        editable_fields = []
        for field in model._meta.get_fields():
            if (
                getattr(field, "editable", False)
                and field.name not in excluded_fields
                and not isinstance(
                    field, (models.OneToOneField, models.ManyToManyField)
                )
                and not isinstance(field, (models.FileField, models.ImageField))
            ):
                if field.get_internal_type() == "ForeignKey":
                    editable_fields.append(field.name + "_id")
                else:
                    editable_fields.append(field.name)

        return editable_fields

    def __get_model_field_names_with_fk_suffix(self, exclude_field_names=[]):

        model = self.model

        list_of_fields = []
        for field in model._meta.fields:
            if field.name not in exclude_field_names:
                if field.get_internal_type() == "ForeignKey":
                    list_of_fields.append(field.name + "_id")
                else:
                    list_of_fields.append(field.name)
        return list_of_fields

    def __rename_fk_fields(self, df):
        model = self.model
        for field in model._meta.fields:
            if field.get_internal_type() == "ForeignKey":
                field_name = field.name
                if field_name in df.columns:
                    df.rename(
                        columns={field.name: field.name + "_id"}, inplace=True)
        return df

    def __check_fields_are_valid(self, df):
        """
        Given a Django model class and a dataframe, check if the dataframe columns match the model fields.
        """

        model = self.model

        df.rename(columns=Utils.camel_to_snake, inplace=True)
        df = self.__rename_fk_fields(df)
        df_columns = set(df.columns)
        if "id" not in df_columns:
            model_fields = set(
                self.__get_model_field_names_with_fk_suffix(
                    exclude_field_names=["id"])
            )
        else:
            model_fields = set(self.__get_model_field_names_with_fk_suffix())
        print(model_fields, df_columns)
        if not (df_columns.issubset(model_fields)):
            raise Exception("Columns in df are not a subset of model fields: %s, on model: %s" % (
                df_columns.difference(model_fields), model.__name__))

        model_fields_in_df = df_columns.intersection(model_fields)
        df = df[list(model_fields_in_df)]
        return df

    def __get_model_field_types(self):

        model = self.model

        model_fields = {}
        for field in model._meta.fields:
            field_class = field.__class__
            if field.get_internal_type() == "ForeignKey":
                model_fields[field.name + "_id"] = field_class
            else:
                model_fields[field.name] = field_class
        return model_fields

    def __check_n_update_df_as_per_model(self, df):

        model = self.model

        # Field type to Pandas dtype mapping
        field_to_dtype = {
            models.ForeignKey: "Int64",
            models.IntegerField: "Int64",
            models.FloatField: "float64",
            models.BooleanField: "bool",
            models.DateTimeField: "datetime64[ns]",
            models.DateField: "datetime64[ns]",
            models.CharField: "str",
            models.TextField: "str",
            models.DurationField: "timedelta64[ns]",
            models.DecimalField: "float64",
            models.PositiveIntegerField: "Int64",
            models.PositiveSmallIntegerField: "Int64",
            models.BigIntegerField: "Int64",
            models.SmallIntegerField: "Int64",
            models.AutoField: "Int64",
            models.BigAutoField: "Int64",
            models.EmailField: "str",
            models.URLField: "str",
            models.FileField: "str",
            models.ImageField: "str",
            models.UUIDField: "str",
            models.BinaryField: "bytes",
        }
        model_fields = self.__get_model_field_types()
        for field_name in df.columns:
            field_type = model_fields[field_name]
            conversion = field_to_dtype.get(field_type)
            if not conversion:
                raise Exception(f"Field type {field_type} not supported")
            if callable(conversion):
                df[field_name] = conversion(df[field_name])
            else:
                if field_type == models.ForeignKey:
                    col_dtype = df[field_name].dtype
                    # If column dtype is not object, convert to Int64
                    if col_dtype != "object":
                        df[field_name] = df[field_name].astype("Int64")
                elif field_type == models.CharField:
                    field = model._meta.get_field(field_name)
                    df[field_name] = df[field_name].astype("str")
                    if hasattr(field, "choices") and field.choices:
                        df[field_name] = df[field_name].str.lower()
                elif field_type == models.DateTimeField:
                    df[field_name] = pd.to_datetime(
                        df[field_name]).dt.tz_localize(None)
                else:
                    df[field_name] = df[field_name].astype(conversion)

        return df

    def __update_null_or_default_values(self, df):

        model = self.model

        # Identify fields from the model and their types, foreign keys with _id suffix
        model_fields = self.__get_model_field_types()
        for column in df.columns:
            field = model_fields[column]
            # Handle DateTimeField and DateField
            if isinstance(field, (models.DateTimeField, models.DateField)):
                df[column] = df[column].where(pd.notna(df[column]), None)
            # Handle FloatField and DecimalField
            elif isinstance(field, (models.FloatField, models.DecimalField)):
                default_value = (
                    field.default if field.default != models.NOT_PROVIDED else None
                )
                if default_value is not None:
                    df[column] = df[column].fillna(
                        default_value).astype("float64")
                else:
                    # Handle the case where default_value is None, maybe fill with 0, or use another method
                    df[column] = df[column].fillna(0).astype("float64")
            # Handle IntegerFields
            elif isinstance(
                field,
                (
                    models.IntegerField,
                    models.PositiveIntegerField,
                    models.PositiveSmallIntegerField,
                    models.BigIntegerField,
                    models.SmallIntegerField,
                ),
            ):
                default_value = (
                    field.default if field.default != models.NOT_PROVIDED else None
                )
                if default_value is None:
                    # Handle the case where default_value is None, maybe fill with 0, or use another method
                    df[column] = df[column].fillna(0).astype("Int64")
                else:
                    df[column] = (
                        df[column].fillna(default_value).astype("Int64")
                    )  # Use 'Int64' to keep NaN as <NA>
            # Handle CharField and TextField
            elif isinstance(field, (models.CharField, models.TextField)):
                default_value = (
                    field.default if field.default != models.NOT_PROVIDED else ""
                )
                df[column] = df[column].fillna(default_value)
            # Handle BooleanField (Note: Assumes False for NaN. Adjust if needed.)
            elif isinstance(field, models.BooleanField):
                df[column] = df[column].fillna(False)

            # ... You can continue for other field types if needed
        return df

    def __check_unique_constraints(self, df):
        """
        Given a Django model class and a dataframe, check if the dataframe contains duplicate records.
        """

        if "id" in df.columns:
            # check id is unique
            if df["id"].notnull().all() and df["id"].duplicated().any():
                raise ValueError(
                    f"Duplicate values found for field id. Please check the dataframe."
                )
        else:
            unique_constraints = self.__get_unique_field_tuples()
            for fields in unique_constraints:
                # Create a mask to filter out rows where any of the fields are None

                should_check = True
                for field in fields:
                    if field not in df.columns:
                        should_check = False
                        break
                if not should_check:
                    continue
                non_null_mask = df[list(fields)].notnull().all(axis=1)

                # Check for duplicates in rows where all fields have non-null values
                duplicates = df[non_null_mask].duplicated(
                    subset=fields, keep=False)

                if duplicates.any():
                    raise ValueError(
                        f"Duplicate values found for fields {fields}. Please check the dataframe."
                    )

    def __add_id(self, df):
        """
        Fetch IDs from the database based on unique field tuples and add them to the dataframe.
        """

        model = self.model

        # Convert fetched database records into a dataframe
        if not (model.objects.exists()):
            df["id"] = None
            return df
        unique_field_tuples = self.__get_unique_field_tuples()
        temp_id_cols = []  # To keep track of all temporary ID columns
        for unique_fields in unique_field_tuples:
            should_check = True
            for field in unique_fields:
                if field not in df.columns:
                    should_check = False
                    break
            if not should_check:
                continue
            # Create a temporary 'match' column for merging
            match_col_name = "_".join(unique_fields) + "_match"
            id_col_name = "_".join(unique_fields) + "_id"
            df[match_col_name] = (
                df[list(unique_fields)].astype(str).agg("_".join, axis=1)
            )
            db_records = pd.DataFrame(
                list(model.objects.values(*list((unique_fields) + ("id",))))
            )
            db_records[match_col_name] = (
                db_records[list(unique_fields)].astype(
                    str).agg("_".join, axis=1)
            )
            df = df.merge(
                db_records[[match_col_name, "id"]
                           ], on=match_col_name, how="left"
            )
            df[id_col_name] = df["id"]
            temp_id_cols.append(id_col_name)
            df.drop(columns=[match_col_name, "id"], inplace=True)
        # Ensure all temporary ID columns have consistent values
        first_id_col = temp_id_cols[0]
        for id_col in temp_id_cols[1:]:
            # Check if both columns are identical, including NaN and non-numeric values
            _df = df[df[first_id_col] != df[id_col]]
            if (
                not _df.empty
                and _df[first_id_col].notna().all()
                and _df[id_col].notna().all()
            ):
                raise ValueError(
                    f"Discrepancy found in ID values between {first_id_col} and {id_col}"
                )
        df["id"] = df[first_id_col]
        df.drop(columns=temp_id_cols, inplace=True)
        return df

    def __insert_or_update_df(self, df):

        def _convert_date_col_to_str(df):
            datetime_fields = [
                field
                for field, field_type in self.__get_model_field_types().items()
                if isinstance(field_type, (models.DateTimeField))
            ]
            date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns
            for col in date_cols:
                if col in datetime_fields:
                    df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    df[col] = df[col].dt.strftime("%Y-%m-%d")
                df[col] = df[col].astype(str)
                df[col] = df[col].replace(["NaT", "nan"], None)
            return df

        """
        Insert new records or update existing records in the database from the dataframe.
        """

        model = self.model

        df = self.__check_n_update_df_as_per_model(df)

        # Convert datetime fields to string
        df = _convert_date_col_to_str(df)
        editable_fields = self.__get_editable_fields()
        relevant_fields = list(set(df.columns) & set(editable_fields))
        # Identify new records (rows with NaN or missing IDs)
        BATCH_SIZE = 2000  # Define batch size
        for start_idx in range(0, len(df), BATCH_SIZE):
            print(start_idx / len(df) * 100, "%")
            end_idx = start_idx + BATCH_SIZE
            batch_df = df.iloc[start_idx:end_idx]

            # Identify new records (rows with NaN or missing IDs) in the current batch
            new_records = batch_df[batch_df["id"].isna()]
            new_records.drop(columns=["id"], inplace=True)
            new_objs_to_insert = [
                model(**record) for record in new_records.to_dict("records")
            ]

            # Prepare existing records for update in the current batch
            existing_records = batch_df.dropna(subset=["id"])
            objs_to_update = [
                model(
                    id=record["id"],
                    **{field: record[field] for field in relevant_fields},
                )
                for record in existing_records.to_dict("records")
            ]

            with transaction.atomic():
                # Bulk create new records
                if new_objs_to_insert:
                    model.objects.bulk_create(new_objs_to_insert)
                # Bulk update existing records
                if objs_to_update and relevant_fields:
                    model.objects.bulk_update(
                        objs_to_update, fields=relevant_fields)

    def __update_foreign_key_values(self, df, fk_strict=True):

        model = self.model
        # Create a dictionary to store unique field tuples for each ForeignKey
        fk_unique_field_tuples = {}
        # Loop through fields in the model to gather unique field tuples for ForeignKey fields

        if "id" in df.columns:
            df["id_copy"] = df["id"]
            df.drop(columns=["id"], inplace=True)

        for field in model._meta.fields:
            if isinstance(field, models.ForeignKey):
                fk_model = field.related_model
                fk_field_name_in_model = field.name
                # Check if the field exists in the DataFrame
                fk_field_name_in_df = fk_field_name_in_model + "_id"
                if fk_field_name_in_df not in df.columns:
                    continue
                # Check the first non-empty dictionary value for the field
                non_empty_values = df[fk_field_name_in_df][
                    df[fk_field_name_in_df].apply(
                        lambda x: isinstance(x, dict) and bool(x)
                    )
                ]
                first_non_empty_dict = (
                    non_empty_values.iloc[0] if not non_empty_values.empty else None
                )
                if not first_non_empty_dict or not isinstance(
                    first_non_empty_dict, dict
                ):
                    continue
                # Identify unique field tuples for the ForeignKey model
                unique_field_tuples = self.__get_unique_field_tuples(fk_model)
                # Store the unique field tuples in the dictionary
                fk_unique_field_tuples[fk_field_name_in_df] = {
                    "model": fk_model,
                    "matching_tuple": None,
                }
                # Check if dictionary keys match one of the unique_field_tuples
                for uft in unique_field_tuples:
                    if set(first_non_empty_dict.keys()) == set(uft):
                        fk_unique_field_tuples[fk_field_name_in_df][
                            "matching_tuple"
                        ] = uft
                        break

        for fk_field_name, fk_info in fk_unique_field_tuples.items():
            if not fk_info["matching_tuple"]:
                raise ValueError(
                    f"The provided dictionary for field {fk_field_name} does not match any unique constraint of the related model."
                )
            fk_model = fk_info["model"]
            matching_tuple = fk_info["matching_tuple"]
            matching_tuple = list(matching_tuple)

            # Fetch all related objects and convert them into a DataFrame
            related_objs_df = pd.DataFrame(list(fk_model.objects.values()))

            # Create a temporary 'match' column for merging
            match_col_name = "_".join(matching_tuple) + "_match"
            df[match_col_name] = df[fk_field_name].apply(
                lambda x: (
                    "_".join([str(x.get(field)) for field in matching_tuple])
                    if x
                    else None
                )
            )
            related_objs_df[match_col_name] = (
                related_objs_df[matching_tuple].astype(
                    str).agg("_".join, axis=1)
            )

            # Merge the DataFrames on the match column to get the IDs
            df = df.merge(
                related_objs_df[[match_col_name, "id"]
                                ], on=match_col_name, how="left"
            )

            if fk_strict:
                __df = df[df["id"].isnull() & (df[fk_field_name].apply(
                    lambda x: isinstance(x, dict) and bool(x)))]
                if len(__df) > 0:
                    raise ValueError(
                        "Foreign key values not found in the database, for field: %s. Top 5 values provided in the DataFrame: %s"
                        % (
                            fk_field_name,
                            df[df["id"].isnull() & df[fk_field_name].notnull()
                               ][fk_field_name].head()
                        )
                    )

            df[fk_field_name] = df["id"]
            df.drop(columns=[match_col_name, "id"], inplace=True)

        if "id_copy" in df.columns:
            df.rename(columns={"id_copy": "id"}, inplace=True)

        return df

    def __get_non_nullable_fields(self):
        """Get all field names from a Django model where null=False."""
        model = self.model
        return [
            (
                field.name
                if not field.get_internal_type() == "ForeignKey"
                else field.name + "_id"
            )
            for field in model._meta.fields
            if getattr(field, "null") == False and not field.name in ["id"]
        ]

    def __check_null_fields_in_df(self, df):
        """Check if any non-nullable fields are null in the DataFrame."""
        non_nullable_fields = self.__get_non_nullable_fields()
        for field in non_nullable_fields:
            if field in df.columns:
                null_values = df[field].isnull().any()
                if null_values:
                    raise ValueError(
                        f"Null values found in non-nullable fields: {field}"
                    )

    def sync(self, df, *args, **kwargs):
        """
        Sync the given dataframe with the model.

        Parameters:
        df (pandas.DataFrame): The dataframe to be synced.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
            fk_strict (bool): If True, enforces strict foreign key constraints.
                              This means that any foreign key values provided in the dataframe
                              must already exist in the related table. If False, the foreign key
                              values can be None or default values will be used. Default is True.

        Raises:
        ValueError: If the dataframe does not contain a column named 'id' and does not have
                    any unique constraints.

        Notes:
        - The function first checks if the dataframe is empty. If it is, the function returns immediately.
        - The dataframe is then validated and updated to match the model's fields.
        - Foreign key values are updated based on the fk_strict flag.
        - Unique constraints are checked.
        - If the dataframe does not contain an 'id' column, one is added.
        - Finally, the dataframe is inserted or updated in the model.
        """
        fk_strict = kwargs.get("fk_strict", True)
        print(df)
        model = self.model
        print(model)
        if df.empty:
            return
        if "id" not in df.columns and not (self.__get_unique_field_tuples()):
            raise ValueError(
                "The provided dataframe does not contain a column named 'id' and does not have any unique constraints. model: {}".format(
                    model
                )
            )
        now = datetime.now()
        df = self.__check_fields_are_valid(df)
        self.__check_null_fields_in_df(df)
        time_taken_in_seconds = (datetime.now() - now).total_seconds()
        print("checking fields are valid", time_taken_in_seconds)
        df = self.__check_n_update_df_as_per_model(df)
        time_taken_in_seconds = (datetime.now() - now).total_seconds()
        print("checking n updating df as per model", time_taken_in_seconds)
        df = self.__update_null_or_default_values(df)
        time_taken_in_seconds = (datetime.now() - now).total_seconds()
        print("updating null or default values", time_taken_in_seconds)
        df = self.__update_foreign_key_values(df, fk_strict=fk_strict)
        time_taken_in_seconds = (datetime.now() - now).total_seconds()
        print("updating foreign key values", time_taken_in_seconds)
        self.__check_unique_constraints(df)
        time_taken_in_seconds = (datetime.now() - now).total_seconds()
        print("checking unique constraints", time_taken_in_seconds)
        if "id" not in df.columns:
            df = self.__add_id(df)
        time_taken_in_seconds = (datetime.now() - now).total_seconds()
        print("adding id", time_taken_in_seconds)
        self.__insert_or_update_df(df)
        time_taken_in_seconds = (datetime.now() - now).total_seconds()
        print("inserting or updating df", time_taken_in_seconds)
