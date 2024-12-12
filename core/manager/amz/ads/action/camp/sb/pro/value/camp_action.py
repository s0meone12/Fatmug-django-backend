import pandas as pd
from core.models import SbProCampaignAction
from ........base import CheckQSMeta
from .main import SbProCampActionValueManager


class SbProCampActionSubManagerSbProActionValue(metaclass=CheckQSMeta):
    def __init__(self, manager: SbProCampActionValueManager):
        self.manager = manager
        self.model = SbProCampaignAction
        
    def get_qs(self, qs=None):
        return self.model.objects.all()

    def campaign_update_action_values(self, qs=None):
        """
        This method will update the action_values for campaigns.
        """
        qs = self.get_qs(qs=qs)
        actions = qs.filter(state__iexact='draft').values("id", "disc_campaign__campaign__name", "disc_campaign__name", "disc_campaign__campaign__budget", "disc_campaign__budget")
        l=[]
        df=pd.DataFrame(actions)
        for i in range(len(df)):
            l.append({"action": actions[i]["id"], "name": "campaign_name", "old_value": actions[i]
                     ["disc_campaign__campaign__name"], "new_value": actions[i]["disc_campaign__name"]})
            l.append({"action": actions[i]["id"], "name": "budget", "old_value": actions[i]
                     ["disc_campaign__campaign__budget"], "new_value": actions[i]["disc_campaign__budget"]})
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
