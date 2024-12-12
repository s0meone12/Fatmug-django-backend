from ......base import CheckQSMeta
import pandas as pd
from core.models import AmzSku
from ..mixin import AmzSkuSubManagerMixinAdCamp


class AmzSkuSubManagerSpCamp(AmzSkuSubManagerMixinAdCamp, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def get_opt_keyword_campaigns(self, qs=None) -> pd.DataFrame:
        return self._get_campaigns('sp_opt_keyword', qs=qs)

    def get_opt_target_campaigns(self, qs=None) -> pd.DataFrame:
        return self._get_campaigns('sp_opt_target', qs=qs)

    def get_fetch_keyword_campaigns(self, qs=None) -> pd.DataFrame:
        return self._get_campaigns('sp_fetch_keyword', qs=qs)

    def get_fetch_target_campaigns(self, qs=None) -> pd.DataFrame:
        return self._get_campaigns('sp_fetch_target', qs=qs)
