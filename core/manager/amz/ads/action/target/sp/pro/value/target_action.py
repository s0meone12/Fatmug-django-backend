import pandas as pd
from ........base import CheckQSMeta
from core.models import SpProTgtAction
from .main import SpProTargActionValueManager


class SpProTargActionSubManagerSpProActionValue(metaclass=CheckQSMeta):
    def __init__(self, manager: SpProTargActionValueManager):
        self.manager = manager
        self.model = SpProTgtAction
    
    def get_qs(self, qs=None):
        return self.model.objects.all()

    def target_update_action_values(self, qs=None):
        """
        This method will store the action value of updation of the live targets in action values mode
        """
        qs = self.get_qs(qs=qs)
        l=[]
        actions = qs.filter(state__iexact='draft').values('id', 'disc_target__bid', 'disc_target__target__bid')
        df = pd.DataFrame(list(actions))
        for i in range(len(df)):
            l.append({
                      "action": df["id"][i], 
                      "old_value": df["disc_target__target__bid"][i],
                      "new_value": df["disc_target__bid"][i]
                      })
        df=pd.DataFrame(l)
        return self._manager.dfdb.sync(df)
