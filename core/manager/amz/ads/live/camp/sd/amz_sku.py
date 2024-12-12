from ......base import CheckQSMeta
import pandas as pd
from core.models import AmzSku
from ..mixin import AmzSkuSubManagerMixinAdCamp


class AmzSkuSubManagerSdCamp(AmzSkuSubManagerMixinAdCamp, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def get_target_campaigns(self, qs=None) -> pd.DataFrame:
        return self._get_campaigns('sd_target', qs=qs)
