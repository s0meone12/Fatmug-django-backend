from django.db import models
from core.models.inheritance import BaseModel
from core.manager import AmzSettlementAmountDescriptionManager


class AmzSettlementAmountDescription(BaseModel):
    name = models.CharField(
        max_length=255, unique=True, verbose_name="Amount Description Name"
    )

    manager = AmzSettlementAmountDescriptionManager()

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_by_name_values(cls, name_set):
        """
        Get existing AmzSettlementAmountDescription records for a set of names or create new ones if they don't exist.
        :param name_set: Set of names to look for or create.
        :return: QuerySet of AmzSettlementAmountDescription instances.
        """
        existing_objects = cls.objects.filter(name__in=name_set)

        # Determine which names are not in the database
        existing_names = set(obj.name for obj in existing_objects)
        new_names = name_set - existing_names

        # Create records for the new names
        cls.objects.bulk_create([cls(name=name) for name in new_names])

    class Meta:
        verbose_name = "Amazon Settlement Amount Description"
        verbose_name_plural = "Amazon Settlement Amount Descriptions"
        indexes = [models.Index(fields=["name"])]
