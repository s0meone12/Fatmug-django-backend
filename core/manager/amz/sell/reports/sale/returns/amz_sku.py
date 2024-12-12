from core.manager.base import CheckQSMeta
from core.models import AmzSku
import pandas as pd
from django.db.models import F, Sum, Window
from datetime import datetime, timedelta


class AmzSkuSubManagerAmzSaleReturn(metaclass=CheckQSMeta):
    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku
        self.days = 90

    def get_qs(self, qs=None):
        return self.manager.filter(sku__in=qs)

    def count(self, qs=None):
        return pd.DataFrame(self.get_qs(qs=qs).filter(return_datetime__gt=(datetime.now()-timedelta(days=self.days))).annotate(
            count=Window(
                expression=Sum('quantity'),
                partition_by=[F('sku'), F('detailed_disposition')],
            )
        ).distinct('sku', 'detailed_disposition').values('sku', 'detailed_disposition', 'count')).sort_values('count', ascending=False)
