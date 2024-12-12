from ..main import SpDiscFetchKeyCampManager
from core.models import AmzSpAdsCamp


class AdsInitialAssociatorSubManagerSpDiscFetchKeyCamp:
    def __init__(self, manager: SpDiscFetchKeyCampManager):
        self.manager = manager

    def _run(self):
        df = AmzSpAdsCamp.manager.amz_sku.get_fetch_keyword_campaigns()
        self.manager.dfdb.sync(df)
