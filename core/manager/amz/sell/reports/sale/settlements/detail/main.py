from core.manager.base import BaseManager


class AmzSettlementDetailManager(BaseManager):
    def __init__(self, *args, **kwargs):
        # There is no API interaction of this model. This API manager needs to move to the AmzSettlement Model where the report fething happens
        super().__init__(*args, **kwargs)
        self._amz_sku = None

    @property
    def amz_sku(self):
        if not self._amz_sku:
            from .amz_sku import AmzSkuSubManagerAmzSettlementDetail
            self._amz_sku = AmzSkuSubManagerAmzSettlementDetail(self)
        return self._amz_sku
