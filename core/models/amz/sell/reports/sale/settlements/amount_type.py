from django.db import models
from core.models.inheritance import BaseModel

class AmzSettlementAmountType(BaseModel):
    name = models.CharField(max_length=50, unique=True,
                            verbose_name="Amount Type Name")

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_by_name_values(cls, name_set):
        """
        Get existing AmzSettlementAmountType records for a set of names or create new ones if they don't exist.
        :param name_set: Set of names to look for or create.
        :return: QuerySet of AmzSettlementAmountType instances.
        """
        existing_objects = cls.objects.filter(name__in=name_set)

        # Determine which names are not in the database
        existing_names = set(obj.name for obj in existing_objects)
        new_names = name_set - existing_names

        # Create records for the new names
        cls.objects.bulk_create([cls(name=name) for name in new_names])

    class Meta:
        verbose_name = "Amazon Settlement Amount Type"
        verbose_name_plural = "Amazon Settlement Amount Types"
        indexes = [models.Index(fields=["name"])]
