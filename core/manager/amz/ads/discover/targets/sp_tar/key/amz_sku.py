from .......base import CheckQSMeta
from core.models import AmzSku, AmzSkuDiscKey
from ...mixin import AmzSkuSubManagerMixinDiscTarget


class AmzSkuSubManagerSPDiscKeyTgt(AmzSkuSubManagerMixinDiscTarget, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def get_qs(self, qs=None):
        return self.manager.filter(sku__in=qs)

    def discover(self, qs=None):
        self._discover(qs=qs, model=AmzSkuDiscKey,
                       method='pending_sp_dicovery')
