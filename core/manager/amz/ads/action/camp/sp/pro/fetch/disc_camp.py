from core.models import SpDiscFetchProCamp
from ........base import CheckQSMeta
import pandas as pd
from .main import SpProFetchCampActionManager


class SpProFetchCampSubManagerSpProFetchAction(metaclass=CheckQSMeta):
    def __init__(self, manager: SpProFetchCampActionManager):
        self.manager = manager
        self.model = SpDiscFetchProCamp

    def get_qs(self, qs=None):
        return self.model.objects.all()

    def campaign_update_action(self, qs=None):
        qs = self.get_qs(qs=qs)
        id_list = qs.filter(campaign__isnull=False, campaign__state__iexact='enabled',
                            campaign__amz_sku__isnull=False).values_list("id", flat=True)
        df = pd.DataFrame(
            [{"disc_campaign": i, "type": "archive", "state": "draft"} for i in id_list])
        df["id"] = None
        return self.manager.dfdb.sync(df)
