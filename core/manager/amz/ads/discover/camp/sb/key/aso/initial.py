from ..main import AmzSbDiscKeyCampManager
from core.models import AmzSbAdsCamp


class AdsInitialAssociatorSubManagerAmzSbDiscKeyCamp:
    def __init__(self, manager: AmzSbDiscKeyCampManager):
        self.manager = manager

    def _run(self):
        df = AmzSbAdsCamp.manager.amz_sku.get_keyword_campaigns()
        self.manager.dfdb.sync(df)

