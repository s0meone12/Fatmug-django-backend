from ..main import AmzSpDiscProCampManager
from core.models import AmzSpAdsCamp


class AdsInitialAssociatorSubManagerAmzSpDiscProCamp:
    def __init__(self, manager: AmzSpDiscProCampManager):
        self.manager = manager

    def _run(self):
        df = AmzSpAdsCamp.manager.amz_sku.get_opt_target_campaigns()
        self.manager.dfdb.sync(df)
