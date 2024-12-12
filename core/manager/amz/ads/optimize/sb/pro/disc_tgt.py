from ...mixin import DiscTgtSubManagerMixinTgtOpt
from core.models import SBDiscProTgt


class SBDiscProTgtSubManagerSbProTgtOpt(DiscTgtSubManagerMixinTgtOpt):
    """
    SubManager for DiscProTarget optimization.
    """
    def __init__(self, manager):
        self.manager = manager
        self.model = SBDiscProTgt

    def set_max_bid(self):
        """
        Set max bid for the product targets with sales.
        """
        df = self._set_max_bid('target')
        self.model.manager.dfdb.sync(df)
        return len(df)

    def set_muted_on_unviable_and_optimize_bid(self):
        """
        Set muted_on_unviable for the product targets with spend but no sales.
        """
        df = self._set_muted_on_unviable_and_optimize_bid('target')
        self.model.manager.dfdb.sync(df)
        return len(df)

    def optimize_bid_with_no_spend(self):
        """
        Optimize bid for the product targets with no spend.
        """
        df = self._optimize_bid_with_no_spend('target')
        self.model.manager.dfdb.sync(df)
        return len(df)

    def bid_calcu_for_new_targ(self):
        """
        Calculate bid for the new product targets.
        """
        df = self._bid_calcu_for_new_targ('target')
        self.model.manager.dfdb.sync(df)
        return len(df)
