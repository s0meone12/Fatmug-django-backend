from .......base import CheckQSMeta
from core.models import AmzSkuDiscKey
from .main import SBDiscKeyTgtManager


class AmzSkuDiscKeySubManagerSBDiscKeyTgt(metaclass=CheckQSMeta):

    def __init__(self, manager: SBDiscKeyTgtManager):
        self.manager = manager
        self.model = AmzSkuDiscKey

    def _no_of_new_disc_targets(self, qs) -> int:
        """
        This method will count the number of new discover target for the sku
        """
        discovered_keyword_targets = self.manager.filter(
            keyword__isnull=True, disc_campaign__isnull=True,
            sku_disc_tgt__in=qs).count()
        return discovered_keyword_targets
    
