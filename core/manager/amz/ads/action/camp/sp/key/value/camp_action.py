import pandas as pd
from core.models import SpKeyCampaignAction
from ........base import CheckQSMeta
from .main import SpKeyCampActionValueManager


class SpKeyCampActionSubManagerSpKeyActionValue(metaclass=CheckQSMeta):
    def __init__(self, manager: SpKeyCampActionValueManager):
        self.manager = manager
        self.model = SpKeyCampaignAction
  
    def get_qs(self, qs=None):
        return self.model.objects.all()

    def campaign_update_action_values(self, qs=None):
        """
        This method will update the action_values for campaigns.
        """
        qs = self.get_qs(qs=qs)
        actions = qs.filter(state__iexact='draft').values("id", "disc_campaign__campaign__name", "disc_campaign__name", "disc_campaign__budget", "disc_campaign__campaign__budget")
        df = pd.DataFrame(actions)
        l = []
        for i in range(len(df)):
            l.append({"action": df["id"][i], "name": "campaign_name",
                     "old_value": df["disc_campaign__campaign__name"][i], "new_value": df["disc_campaign__name"][i]})
            l.append({"action": df["id"][i], "name": "budget", "old_value": df["disc_campaign__campaign__budget"]
                     [i], "new_value": df["disc_campaign__budget"][i]})
        df = pd.DataFrame(l)
        df["id"] = None
        return self.manager.dfdb.sync(df)

    def get_values(self, qs=None) -> pd.DataFrame:
        """
        This method will get the action_values for campaigns.
        """
        action_value_qs = self.manager.filter(action__in=qs)
        df = pd.DataFrame(action_value_qs.values(
            'action_id', 'name', 'new_value', 'action__disc_campaign__campaign_id_code'))
        return df
