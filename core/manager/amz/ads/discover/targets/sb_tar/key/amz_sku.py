from .......base import CheckQSMeta
from core.models import AmzSku, AmzSkuDiscKey
from ...mixin import AmzSkuSubManagerMixinDiscTarget
from .main import SBDiscKeyTgtManager


class AmzSkuSubManagerSBDiscKeyTgt(AmzSkuSubManagerMixinDiscTarget, metaclass=CheckQSMeta):

    def __init__(self, manager: SBDiscKeyTgtManager):
        self.manager = manager
        self.model = AmzSku

    def get_qs(self, qs=None):
        return self.manager.filter(sku__in=qs)

    def discover(self, qs=None):
        self._discover(qs=qs, model=AmzSkuDiscKey,
                       method='pending_sb_dicovery')
