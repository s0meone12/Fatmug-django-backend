import pandas as pd
from ........base import CheckQSMeta
from core.models import SBDiscKeyTgt
from .main import SbKeyTargActionManager


class SbKeyTargetSubManagerSbKeyAction(metaclass=CheckQSMeta):
    def __init__(self, manager: SbKeyTargActionManager):
        self.manager = manager
        self.model = SBDiscKeyTgt
    
    def get_qs(self, qs=None):
        return self.model.objects.all()

    def target_update_action(self, qs=None):
        """
        This method will store the action of updation of the live targets in action model, only bid updation is allow
        """
        qs = self.get_qs(qs=qs)
        id_list = qs.filter(keyword__isnull=False, keyword_id_code__isnull=False).values_list('id', flat=True)
        df=pd.DataFrame([{"disc_target": i, "state": "draft"} for i in id_list])
        df['id'] = None
        return self.manager.dfdb.sync(df)
