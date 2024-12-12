import pandas as pd
from core.models import SbKeyCampaignAction
from ........base import CheckQSMeta
from .main import SbKeyCampActionValueManager


class SbKeyCampActionSubManagerSbKeyActionValue(metaclass=CheckQSMeta):
    def __init__(self, manager: SbKeyCampActionValueManager):
        self.manager = manager
        self.model = SbKeyCampaignAction

    def get_qs(self, qs=None):
        return self.model.objects.all()

    def campaign_update_action_values(self, qs=None):
        """
        This method will update the action_values for campaigns.
        """
        qs = self.get_qs(qs=qs)
        actions = qs.filter(state__iexact='draft').values("id", "disc_campaign__campaign__name", "disc_campaign__name", "disc_campaign__budget", "disc_campaign__campaign__budget")
        l = []
        df = pd.DataFrame(actions)
        for i in range(len(df)):
            l.append({
                "action": df["id"][i],
                "name": "campaign_name",
                "old_value": df["disc_campaign__campaign__name"][i],
                "new_value": df["disc_campaign__name"][i]
            })
            l.append({
                "action": df["id"][i],
                "name": "budget",
                "old_value": df["disc_campaign__campaign__budget"][i],
                "new_value": df["disc_campaign__budget"][i]
            })
        df = pd.DataFrame(l)
        df["id"] = None
        return self.manager.dfdb.sync(df)

    def get_values(self, qs=None):
        """
        This method will return the action_values for campaigns.
        """
        action_value_qs = self.manager.filter(action__in=qs)
        df = pd.DataFrame(action_value_qs.values(
            'action_id', 'name', 'new_value', 'action__disc_campaign__campaign_id_code'))
        return df
