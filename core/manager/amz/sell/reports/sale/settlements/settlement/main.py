from .......base import BaseManager


class AmzSettlementManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = None

    @property
    def api(self):
        if self._api is None:
            from .api import ApiSubManagerAmzSettlement
            self._api = ApiSubManagerAmzSettlement(self)
        return self._api
