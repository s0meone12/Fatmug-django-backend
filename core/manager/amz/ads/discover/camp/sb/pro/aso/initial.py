from ..main import AmzSbDiscProCampManager
from core.models import AmzSbAdsCamp


class AdsInitialAssociatorSubManagerAmzSbDiscProCamp:
    def __init__(self, manager: AmzSbDiscProCampManager):
        self.manager = manager

    def _run(self):
        df = AmzSbAdsCamp.manager.amz_sku.get_target_campaigns()
        self.manager.dfdb.sync(df)
