from .......base import CheckQSMeta
from core.models import AmzSku, AmzSkuDiscProTgt
from ...mixin import AmzSkuSubManagerMixinDiscTarget


class AmzSkuSubManagerSPDiscProTgt(AmzSkuSubManagerMixinDiscTarget, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def get_qs(self, qs=None):
        return self.manager.filter(sku__in=qs)

    def discover(self, qs=None):
        self._discover(qs=qs, model=AmzSkuDiscProTgt,
                       method='pending_sp_dicovery')
