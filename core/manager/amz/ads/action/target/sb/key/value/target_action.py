import pandas as pd
from ........base import CheckQSMeta
from core.models import SbKeyTgtAction
from .main import SbKeyTargActionValueManager


class SbKeyTargActionSubManagerSbKeyActionValue(metaclass=CheckQSMeta):
    def __init__(self, manager: SbKeyTargActionValueManager):
        self.manager = manager
        self.model = SbKeyTgtAction

    def get_qs(self, qs=None):
        return self.model.objects.all()
  
    def target_update_action_values(self, qs=None):
        """
        This method will store the action value of updation of the live targets in action values mode
        """
        qs = self.get_qs(qs=qs)
        l=[]
        actions = qs.filter(state__iexact='draft').values('id', 'disc_target__bid', 'disc_target__keyword__bid')
        df = pd.DataFrame(actions)
        for i in range(len(df)):
            l.append({
                "action": df["id"][i],
                "old_value": df["disc_target__keyword__bid"][i],
                "new_value": df["disc_target__bid"][i]
            })
        df = pd.DataFrame(l)
        return self.manager.dfdb.sync(df)
