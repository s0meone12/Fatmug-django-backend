from core.manager.base import BaseManager
import pandas as pd


class AmzSettlementAmountDescriptionManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_direct_fee_types(self):
        l = [
            'Commission',
            'FBA Pick & Pack Fee',
            'FBA Weight Handling Fee',
            'Fixed closing fee',
            'Refund commission',
        ]
        return pd.Series(self.filter(name__in=l).values_list('id', flat=True))
