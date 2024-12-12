from ..main import SpDiscFetchProCampManager
from core.models import AmzSpAdsCamp


class AdsInitialAssociatorSubManagerSpDiscFetchProCamp:
    def __init__(self, manager: SpDiscFetchProCampManager):
        self.manager = manager

    def _run(self):
        df = AmzSpAdsCamp.manager.amz_sku.get_fetch_target_campaigns()
        self.manager.dfdb.sync(df)
