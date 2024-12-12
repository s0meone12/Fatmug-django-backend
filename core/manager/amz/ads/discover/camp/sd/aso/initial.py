from ..main import AmzSdDiscProCampManager
from core.models import AmzSdAdsCamp


class AdsInitialAssociatorSubManagerAmzSbDiscProCamp:
    def __init__(self, manager: AmzSdDiscProCampManager):
        self.manager = manager

    def _run(self):
        df = AmzSdAdsCamp.manager.amz_sku.get_target_campaigns()
        self.manager.dfdb.sync(df)
