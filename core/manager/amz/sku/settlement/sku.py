from decimal import Decimal
from typing import Tuple
from core.manager.base import CheckQSMeta
from core.models import AmzSku
from core.models import AmzSkuSettlement
from django.db.models import F, Sum, Window
import pandas as pd
from .main import AmzSkuSettlementManager


class AmzSkuSubManagerAmzSkuSettlement(metaclass=CheckQSMeta):
    def __init__(self, manager: AmzSkuSettlementManager):
        self.manager = manager
        self.model = AmzSku
        self.exclude = {"Tax", "tax", "IGST", "CGST", "SGST"}

    def get_qs(self, qs=None):
        return self.manager.filter(sku__in=qs)

    def update_values(self, qs=None):
        from core.models import AmzSettlementDetail
        df = AmzSettlementDetail.manager.amz_sku.avg_amounts(qs=qs)
        df.rename(columns={"amount": "avg_amount_value"}, inplace=True)
        self.manager.dfdb.sync(df)

    def get_fees(self, qs=None):
        from core.models import AmzSettlementAmountDescription
        return pd.DataFrame(self.get_qs(qs=qs).filter(
            amount_description__in=AmzSettlementAmountDescription.manager.get_direct_fee_types()).annotate(
                amount=Window(
                    expression=Sum('avg_amount_value'),
                    partition_by=[F('sku')],
                )
        ).distinct('sku').values('sku', 'amount')).sort_values('amount', ascending=True)
