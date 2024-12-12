from .......base import CheckQSMeta
from core.models import AmzSku, SBDiscKeyTgt, SPDiscKeyTgt
from ..mixin import AmzSkuSubManagerMixinAmzSkuDiscTgt


class AmzSkuSubManagerAmzSkuDiscKey(AmzSkuSubManagerMixinAmzSkuDiscTgt, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def discover(self, qs=None):
        self._discover_keywords(qs=qs)

    def pending_sb_dicovery(self, qs=None):
        return self._pending_discovery(qs=qs, model=SBDiscKeyTgt)

    def pending_sp_dicovery(self, qs=None):
        return self._pending_discovery(qs=qs, model=SPDiscKeyTgt)
