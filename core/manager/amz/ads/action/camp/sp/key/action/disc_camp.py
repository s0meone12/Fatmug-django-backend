import pandas as pd
from core.models import SPDiscKeyCamp
from ........base import CheckQSMeta
from .main import SpKeyCampActionManager


class SpKeyCampSubManagerSpKeyAction(metaclass=CheckQSMeta):
    def __init__(self, manager: SpKeyCampActionManager):
        self.manager = manager
        self.model = SPDiscKeyCamp

    def get_qs(self, qs=None):
        return self.model.objects.all()
    
    def campaign_update_action(self, qs=None):
        """
        This method will update the action for campaigns.
        """
        qs = self.get_qs(qs=qs)
        id_list = qs.filter(campaign__isnull=False, campaign__state__iexact='enabled', campaign__amz_sku__isnull=False).values_list("id", flat=True)
        df = pd.DataFrame([{"disc_campaign" : i , "state" : "draft"} for i in id_list])
        df["id"] = None
        return self.manager.dfdb.sync(df)
