from ...mixin import DiscTgtSubManagerMixinTgtOpt
from core.models import SBDiscKeyTgt

class SBDiscKeyTgtSubManagerSbKeyTgtOpt(DiscTgtSubManagerMixinTgtOpt):
    """
    SubManager for DiscKeyTarget optimization.
    """
    def __init__(self, manager):
        self.manager = manager
        self.model = SBDiscKeyTgt

    def set_max_bid(self):
        """
        Set max bid for the keyword targets with sales.
        """
        df = self._set_max_bid('keyword')
        self.model.manager.dfdb.sync(df)
        return len(df)

    def set_muted_on_unviable_and_optimize_bid(self):
        """
        Set muted_on_unviable for the keyword targets with spend but no sales.
        """
        df = self._set_muted_on_unviable_and_optimize_bid('keyword')
        self.model.manager.dfdb.sync(df)
        return len(df)

    def optimize_bid_with_no_spend(self):
        """
        Optimize bid for the keyword targets with no spend.
        """
        df = self._optimize_bid_with_no_spend('keyword')
        self.model.manager.dfdb.sync(df)
        return len(df)
    
    def bid_calcu_for_new_targ(self):
        """
        Calculate bid for the new keyword targets.
        """
        df = self._bid_calcu_for_new_targ('keyword')
        self.model.manager.dfdb.sync(df)
        return len(df)
