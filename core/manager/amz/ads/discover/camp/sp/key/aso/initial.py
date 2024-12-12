from ..main import AmzSpDiscKeyCampManager
from core.models import AmzSpAdsCamp


class AdsInitialAssociatorSubManagerAmzSpDiscKeyCamp:
    def __init__(self, manager: AmzSpDiscKeyCampManager):
        self.manager = manager

    def _run(self):
        df = AmzSpAdsCamp.manager.amz_sku.get_opt_keyword_campaigns()
        self.manager.dfdb.sync(df)
