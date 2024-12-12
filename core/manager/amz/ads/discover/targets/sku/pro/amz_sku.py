from .......base import CheckQSMeta
from core.models import AmzSku, SBDiscProTgt, SPDiscProTgt
from ..mixin import AmzSkuSubManagerMixinAmzSkuDiscTgt


class AmzSkuSubManagerAmzSkuDiscProTgt(AmzSkuSubManagerMixinAmzSkuDiscTgt, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def discover(self, qs=None):
        self._discover_product_targets(qs=qs)

    def pending_sb_dicovery(self, qs=None):
        return self._pending_discovery(qs=qs, model=SBDiscProTgt)

    def pending_sp_dicovery(self, qs=None):
        return self._pending_discovery(qs=qs, model=SPDiscProTgt)
