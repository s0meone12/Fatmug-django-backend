from ......base import CheckQSMeta
import pandas as pd
from core.models import AmzSku
from ..mixin import AmzSkuSubManagerMixinAdCamp


class AmzSkuSubManagerSbCamp(AmzSkuSubManagerMixinAdCamp, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def get_keyword_campaigns(self, qs=None) -> pd.DataFrame:
        return self._get_campaigns('sb_keyword', qs=qs)

    def get_target_campaigns(self, qs=None) -> pd.DataFrame:
        return self._get_campaigns('sb_target', qs=qs)